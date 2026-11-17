"""Validation rung 2 (brief Part E): flat deep-beam floor against Timoshenko beam theory.

A floor strip of span L and depth D (plan dimensions; the floor works in its own plane under
the seismic inertia load) is modelled with S8R membranes and loaded by a uniform line load q.
Reference: Timoshenko beam, simply supported, mid-span deflection
    d_T = 5 q L^4 / (384 E I) + q L^2 / (8 k G A),   I = t D^3 / 12, A = t D, k = 5/6.
The brief's pass mark is 2 %, checked at L/D = 2 to 8 (deep to slender floors) on two meshes.
The load is a body force through the depth and the end supports hold v over the full depth,
which matches the beam model's assumptions; a load on one edge or point supports would add
local effects that beam theory does not describe.
"""
from pathlib import Path

from partA_mechanics.plate_fe import deep_beam

E, NU, T, Q = 33e9, 0.2, 0.06, 10e3
OUT = Path(__file__).parent / "out" / "rung2_deep_beam.txt"


def main():
    G = E / (2 * (1 + NU))
    rows = []
    worst = 0.0
    for ratio in (2, 3, 4, 6, 8):
        D = 6.0
        L = ratio * D
        I, A = T * D ** 3 / 12, T * D
        bend = 5 * Q * L ** 4 / (384 * E * I)
        d_t = bend + Q * L ** 2 / (8 * 5 / 6 * G * A)
        res = []
        for nx, ny in ((8 * ratio, 8), (16 * ratio, 16)):
            res.append(deep_beam(L, D, T, E, NU, Q, nx=nx, ny=ny))
        fe = res[-1]
        e_t = fe / d_t - 1
        worst = max(worst, abs(e_t), abs(res[0] / d_t - 1))
        rows.append(f"L/D {ratio:2d}  FE {fe * 1e3:9.5f} mm (coarse {res[0] * 1e3:9.5f})  "
                    f"Timoshenko {d_t * 1e3:9.5f} ({100 * e_t:+6.2f} %)  shear share {1 - bend / d_t:5.1%}")
    head = [f"Rung 2: deep-beam floor, E = {E:.3g} Pa, nu = {NU}, t = {T} m, D = 6 m, q = {Q:.3g} N/m",
            "mid-span, mid-depth deflection; errors relative to each reference"]
    tail = [f"worst error against Timoshenko, all L/D and both meshes: {100 * worst:.2f} %  ->  "
            f"{'PASS' if worst < 0.02 else 'FAIL'} (limit 2 %)"]
    OUT.write_text("\n".join(head + rows + tail) + "\n")
    print("\n".join(head + rows + tail))


if __name__ == "__main__":
    main()
