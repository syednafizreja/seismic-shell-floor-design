"""X-strut grid against the shell deep beam.

The panel is calibrated to E t and G t of the flat plate. The deep-beam deflection
is not part of that calibration. The pass mark used here is the brief's rung-4
limit, 5%, on that deflection. Rung 2 already checked the Timoshenko formula
itself (0.21%). This file does not rerun rung 2.

Panel size 1 m. Span 12 m, depth 6 m, the L/D = 2 row of rung 2.
"""
from pathlib import Path

from partA_mechanics.plate_fe import deep_beam
from partA_mechanics.reduced import (
    calibrate_panel, panel_Et_Gt, timoshenko_midspan, xstrut_deep_beam)

E, NU, T, Q = 33e9, 0.2, 0.06, 10e3
L, D = 12.0, 6.0
OUT = Path(__file__).parent / "out" / "xstrut_check.txt"


def main():
    G = E / (2 * (1 + NU))
    Et, Gt = E * T, G * T
    d_t = timoshenko_midspan(L, D, Et, Gt, Q)
    d_fe = deep_beam(L, D, T, E, NU, Q, nx=32, ny=16)
    lines = [
        "X-strut diaphragm. Flat plate. Chords and diagonals calibrated on one panel.",
        "The deep-beam deflection is not used in the calibration.",
        f"E = {E:.3g} Pa, nu = {NU}, t = {T} m, L = {L} m, D = {D} m, q = {Q:.3g} N/m",
        f"target Et {Et:.6e} N/m, Gt {Gt:.6e} N/m",
        f"shell mid-span {d_fe * 1e3:.5f} mm, Timoshenko {d_t * 1e3:.5f} mm",
        "panel m   EA chord N    EA diagonal N   back-check Et %   Gt %    X-strut mm   error",
    ]
    worst = 0.0
    for panel in (1.0, 0.5):
        ea_c, ea_d = calibrate_panel(panel, panel, Et, Gt)
        et_b, gt_b = panel_Et_Gt(panel, panel, ea_c, ea_d)
        d_x = xstrut_deep_beam(L, D, ea_c, ea_d, Q, panel)
        e_x = d_x / d_fe - 1
        worst = max(worst, abs(e_x))
        lines.append(
            f"{panel:6.2f}  {ea_c:.6e}  {ea_d:.6e}  {100 * (et_b / Et - 1):+.3e}  "
            f"{100 * (gt_b / Gt - 1):+.3e}  {d_x * 1e3:8.5f}  {100 * e_x:+7.2f} %")
    lines.append(
        f"largest |error| {100 * worst:.2f} %  ->  "
        f"{'PASS' if worst < 0.05 else 'FAIL'} (limit 5 %, the brief's rung-4 deflection limit)")
    lines.append("The 5 % limit is the brief's rung 4. It is not a code clause.")
    OUT.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
