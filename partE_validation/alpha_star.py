"""First alpha* figure.

alpha = K_d / K_f. K_d is the simply-supported Timoshenko stiffness of one bay.
K_f is the ground-storey lateral stiffness of the anchor transverse frame
(ShellBench spec: C40, E = 32.5 GPa, 600 mm columns, beam I factor 2.0 or 1.5).

The pass test is EN 1998-1 4.3.1(4) NOTE, author's copy of BS EN 1998-1:2004,
PDF page 55, printed page 53: the flexible displacement may exceed the rigid one
by at most 10% of the absolute rigid displacement. Author to confirm that sentence.

alpha* is the alpha of the longer bay at which that ratio is 0.10.
H2 says this threshold is the same across aspect ratios. The two-frame case is
20 by the definition of K_d. The seven-frame floor is the test, because the
bays are continuous and the end bays are 6.0 m.

Cracked diaphragm: Et and Gt at half, from 4.3.1(7). Author to confirm that the
half applies to the floor. The frame stiffness is left at the anchor value.
"""
from pathlib import Path

import numpy as np

from partA_mechanics.reduced import beam_on_springs, displacement_excess, kd_timoshenko, timoshenko_midspan

E_FLOOR, NU = 33e9, 0.2
T = 0.06
DEPTH = 7.2 + 6.6 + 7.2
BAYS = (6.0, 6.6, 6.6, 6.6, 6.6, 6.0)
Q = 1.0
LIMIT = 0.10
OUT = Path(__file__).parent / "out" / "alpha_star.txt"
RIB = Path(__file__).parent / "out" / "vault_rib.txt"


def frame_stiffness(height: float, beam_i: float) -> float:
    """Ground-storey stiffness of one transverse frame, in N/m.

    One storey only: base fixed, beam at the floor, horizontal load shared by the
    four column lines. Author to confirm this storey, not the whole frame.
    """
    import openseespy.opensees as ops
    from shellbench.anchor_frame import AXES, build_frame

    fm = build_frame(storey_heights_m=(height,), beam_inertia_factor=beam_i)
    force = 1000.0
    ops.timeSeries("Linear", 1)
    ops.pattern("Plain", 1, 1)
    share = force / len(AXES)
    for ax in AXES:
        ops.load(fm.node[(ax, 1)], share, 0.0, 0.0)
    ops.constraints("Plain")
    ops.numberer("RCM")
    ops.system("BandGeneral")
    ops.test("NormDispIncr", 1.0e-8, 20)
    ops.algorithm("Linear")
    ops.integrator("LoadControl", 1.0)
    ops.analysis("Static")
    if ops.analyze(1) != 0:
        raise RuntimeError("anchor storey did not solve")
    u = np.mean([ops.nodeDisp(fm.node[(ax, 1)], 1) for ax in AXES])
    return force / u * 1.0e3  # kN/m -> N/m


def excess(spans, D, Et, Gt, Kf):
    _, lateral, u_rigid = beam_on_springs(spans, D, Et, Gt, Kf, q=Q, n_per_bay=12)
    return displacement_excess(lateral, u_rigid)


def alpha_of(L, D, Et, Gt, Kf):
    return kd_timoshenko(L, D, Et, Gt) / Kf


def find_star(spans, D, Et, Gt, Kf, L_ref, k_ref):
    """Scale Et and Gt together until the excess is 10%.

    Kf may be one value per frame. alpha* divides by k_ref, the stiffness of
    the frame used in the definition of alpha, which is the middle frame.
    """
    lo, hi = 1e-4, 1e4
    r_lo, r_hi = excess(spans, D, Et * lo, Gt * lo, Kf), excess(spans, D, Et * hi, Gt * hi, Kf)
    if not (r_lo > LIMIT > r_hi):
        raise RuntimeError(f"10% is outside the sweep ({r_lo}, {r_hi})")
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        r = excess(spans, D, Et * mid, Gt * mid, Kf)
        if r > LIMIT:
            lo = mid
        else:
            hi = mid
    s = 0.5 * (lo + hi)
    return float(alpha_of(L_ref, D, Et * s, Gt * s, k_ref)), float(excess(spans, D, Et * s, Gt * s, Kf))


def recorded_rows():
    """Et/(E T) and Gt/(G T) from the printed rows of vault_rib.txt."""
    wanted = (
        ("smooth rise 0.00", "smooth rise 0"),
        ("cross rise 0.00", "cross rise 0"),
        ("smooth rise 0.30", "smooth 0.30"),
        ("cross rise 0.30", "cross 0.30"),
        ("smooth rise 0.60", "smooth 0.60"),
        ("cross rise 0.60", "cross 0.60"),
    )
    rows = []
    for ln in RIB.read_text().splitlines():
        for key, label in wanted:
            if ln.startswith(key):
                # The rise sits in the label. The remainder is t_sh, t_rib, area, Et, Gt.
                nums = [float(p) for p in ln[len(key):].split() if _is_float(p)]
                rows.append((label, nums[3], nums[4]))
    if len(rows) != len(wanted):
        raise RuntimeError(f"expected {len(wanted)} rows in vault_rib.txt, got {len(rows)}")
    return rows


def _is_float(p):
    try:
        float(p)
        return True
    except ValueError:
        return False


def beam_element_check():
    """Two equal frames. alpha* must be 20, because K_d is defined from this deflection."""
    Et, Gt = 1.0e9, 4.0e8
    D, L, Kf = 21.0, 6.6, 1.0e8
    d = timoshenko_midspan(L, D, Et, Gt, Q)
    _, lateral, u_rigid = beam_on_springs((L,), D, Et, Gt, Kf, q=Q, n_per_bay=32)
    rel = float(lateral[len(lateral) // 2] - lateral[0])
    err = rel / d - 1
    star, got = find_star((L,), D, Et, Gt, Kf, L, Kf)
    return err, star, got


def main():
    err, star2, got2 = beam_element_check()
    k_mid = frame_stiffness(4.55, 2.0)
    k_edge = frame_stiffness(4.55, 1.5)
    k_upper = frame_stiffness(3.6, 2.0)
    Et0 = E_FLOOR * T
    Gt0 = E_FLOOR * T / (2 * (1 + NU))
    # Equal K_f on every line, the middle-frame value. Edge case is separate.
    kf_equal = np.full(len(BAYS) + 1, k_mid)
    kf_edge = np.array([k_edge, *([k_mid] * 5), k_edge])
    lines = [
        "alpha = K_d / K_f. K_d from the simply-supported Timoshenko bay. K_f from one anchor frame.",
        "EN 1998-1 4.3.1(4) NOTE: excess of the flexible displacement over the rigid one, limit 10%.",
        "Author's copy, BS EN 1998-1:2004, PDF page 55, printed page 53. Author to confirm.",
        f"beam element against the closed deflection: {100 * err:+.3f} %",
        f"two-frame alpha* {star2:.4f} (excess {got2:.4f}); the definition gives 20",
        f"K_f ground storey h=4.55 m, beam I factor 2.0: {k_mid:.6e} N/m",
        f"K_f same storey, beam I factor 1.5: {k_edge:.6e} N/m",
        f"K_f upper storey h=3.6 m, beam I factor 2.0: {k_upper:.6e} N/m",
        "The alpha* rows use the ground storey and beam I factor 2.0 on every frame line.",
        "layout                         L/D    alpha*",
    ]
    # Real floor, and the same seven lines with the bay length scaled.
    for scale, name in ((1.0, "anchor bays"), (0.5, "bays x 0.5"), (2.0, "bays x 2")):
        spans = tuple(s * scale for s in BAYS)
        Lref = max(spans)
        star, _ = find_star(spans, DEPTH, Et0, Gt0, kf_equal, Lref, k_mid)
        lines.append(f"{name:28s}  {Lref / DEPTH:5.3f}  {star:8.3f}")
    star_e, _ = find_star(BAYS, DEPTH, Et0, Gt0, kf_edge, max(BAYS), k_mid)
    lines.append(f"{'anchor, edge frames softer':28s}  {max(BAYS) / DEPTH:5.3f}  {star_e:8.3f}")
    # Equal bays, several aspect ratios, seven frames so continuity is present.
    lines.append("seven equal bays")
    for ratio in (0.3, 0.5, 1.0, 2.0):
        L = ratio * DEPTH
        spans = (L,) * 6
        star, _ = find_star(spans, DEPTH, Et0, Gt0, kf_equal, L, k_mid)
        lines.append(f"{'equal':28s}  {ratio:5.3f}  {star:8.3f}")
    lines.append("recorded cells on the anchor bays, uncracked Et and Gt, K_f of the ground storey")
    lines.append("case                    Et/ET    Gt/GT     alpha   excess   cracked alpha  cracked excess")
    for label, et_r, gt_r in recorded_rows():
        Et, Gt = et_r * Et0, gt_r * Gt0
        a = alpha_of(max(BAYS), DEPTH, Et, Gt, k_mid)
        r = excess(BAYS, DEPTH, Et, Gt, kf_equal)
        ac = alpha_of(max(BAYS), DEPTH, 0.5 * Et, 0.5 * Gt, k_mid)
        rc = excess(BAYS, DEPTH, 0.5 * Et, 0.5 * Gt, kf_equal)
        lines.append(f"{label:22s}  {et_r:7.5f}  {gt_r:7.5f}  {a:8.2f}  {r:7.4f}  {ac:8.2f}  {rc:7.4f}")
    lines += [
        "Cracked rows use 0.5 Et and 0.5 Gt (4.3.1(7)) and the same K_f. Author to confirm the half.",
        "Depth is 21.0 m, the three transverse spans. A 3 m cell is used only through Et and Gt.",
        "H2 is about whether alpha* above is one number. The two-frame value 20 is not that test.",
    ]
    OUT.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
