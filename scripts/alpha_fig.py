"""Draw the alpha* figure from partE_validation/out/alpha_star.txt.

Left: alpha* of seven equal bays, in the aspect-ratio order of that file.
Right: uncracked displacement excess of the recorded cells on the anchor bays.
Bars start at zero. The 0.10 line is the EN 1998-1 4.3.1(4) NOTE, author's copy.

Run: python scripts/alpha_fig.py
"""
from __future__ import annotations

import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "partE_validation" / "out" / "alpha_star.txt"
OUT = ROOT / "docs" / "img"

# Fixed to the row order in alpha_star.txt. Not sorted by the result.
EQUAL_COLOURS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]
CELL_COLOURS = {
    "smooth rise 0": "#2a78d6",
    "cross rise 0": "#6f8fbf",
    "smooth 0.30": "#eb6834",
    "cross 0.30": "#1baf7a",
    "smooth 0.60": "#eda100",
    "cross 0.60": "#e87ba4",
}
THEMES = {
    "light": {"bg": "#ffffff", "ink": "#0b0b0b", "muted": "#52514e", "faint": "#898781",
              "grid": "#e1e0d9", "spine": "#c3c2b7", "limit": "#9a3b2f"},
    "dark": {"bg": "#0d1117", "ink": "#f0efec", "muted": "#c3c2b7", "faint": "#8f8d86",
             "grid": "#30363d", "spine": "#484f58", "limit": "#f0a39a"},
}


def load():
    text = SRC.read_text(encoding="utf-8")
    equal = []
    grab = False
    for ln in text.splitlines():
        if ln.startswith("seven equal bays"):
            grab = True
            continue
        if grab:
            m = re.match(r"equal\s+([\d.]+)\s+([\d.]+)", ln)
            if not m:
                break
            equal.append((float(m.group(1)), float(m.group(2))))
    cells = []
    grab = False
    for ln in text.splitlines():
        if ln.startswith("case "):
            grab = True
            continue
        if grab:
            if not ln.strip() or ln.startswith("Cracked"):
                break
            m = re.match(
                r"(.+?)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*$",
                ln,
            )
            if not m:
                raise SystemExit(f"could not read row: {ln}")
            cells.append((m.group(1).strip(), float(m.group(5))))
    if len(equal) != 4 or len(cells) != 6:
        raise SystemExit(f"expected 4 aspect ratios and 6 cells, got {len(equal)} and {len(cells)}")
    return equal, cells


def draw(theme: str, equal, cells) -> None:
    c = THEMES[theme]
    plt.rcParams["font.family"] = "Arial"
    fig, axes = plt.subplots(1, 2, figsize=(12.80, 6.40), dpi=100)
    fig.patch.set_facecolor(c["bg"])
    fig.subplots_adjust(left=0.07, right=0.98, top=0.78, bottom=0.22, wspace=0.28)

    ax = axes[0]
    xs = list(range(len(equal)))
    vals = [v for _, v in equal]
    ax.bar(xs, vals, color=EQUAL_COLOURS, width=0.72, zorder=2)
    ax.set_xticks(xs)
    ax.set_xticklabels([f"{r:.1f}" for r, _ in equal])
    for i, v in enumerate(vals):
        ax.text(i, v + max(vals) * 0.02, f"{v:.3f}", ha="center", va="bottom",
                color=c["ink"], fontsize=9)
    ax.set_ylim(0, max(vals) * 1.18)
    ax.set_ylabel("alpha*", color=c["ink"])
    ax.set_xlabel("L/D", color=c["muted"])
    ax.set_title("Seven equal bays", loc="left", color=c["ink"], fontsize=12)

    ax = axes[1]
    xs = list(range(len(cells)))
    excess = [v for _, v in cells]
    colours = [CELL_COLOURS[name] for name, _ in cells]
    ax.bar(xs, excess, color=colours, width=0.72, zorder=2)
    ax.axhline(0.10, color=c["limit"], lw=1.2, zorder=3)
    ax.text(5.45, 0.102, "0.10", color=c["limit"], fontsize=9, ha="left", va="bottom")
    ax.set_xticks(xs)
    ax.set_xticklabels([name.replace(" ", "\n") for name, _ in cells], fontsize=8)
    for i, v in enumerate(excess):
        ax.text(i, v + 0.004, f"{v:.4f}", ha="center", va="bottom", color=c["ink"], fontsize=8)
    ax.set_ylim(0, max(excess) * 1.25)
    ax.set_ylabel("displacement excess", color=c["ink"])
    ax.set_title("Recorded cells, uncracked", loc="left", color=c["ink"], fontsize=12)

    for axis in axes:
        axis.set_facecolor(c["bg"])
        axis.tick_params(colors=c["muted"])
        axis.spines["top"].set_visible(False)
        axis.spines["right"].set_visible(False)
        axis.spines["left"].set_color(c["spine"])
        axis.spines["bottom"].set_color(c["spine"])
        axis.yaxis.grid(True, color=c["grid"], zorder=0)
        axis.set_axisbelow(True)

    fig.text(0.07, 0.90, "alpha* is not one number across aspect ratio",
             color=c["ink"], fontsize=16, fontweight="medium")
    fig.text(0.07, 0.845,
             "Bars start at zero. The 0.10 line is EN 1998-1 4.3.1(4) NOTE, author's copy.",
             color=c["muted"], fontsize=10)
    fig.text(0.07, 0.04, "Data: partE_validation/out/alpha_star.txt. Seven frames. K_f is the anchor ground storey.",
             color=c["faint"], fontsize=9)
    fig.savefig(OUT / f"alpha_{theme}.png", dpi=100)
    plt.close(fig)


def main():
    equal, cells = load()
    for theme in THEMES:
        draw(theme, equal, cells)


if __name__ == "__main__":
    main()
