# One vault bay: in-plane stiffness, a diaphragm ratio, and gravity

Syed Nafiz Reja Hasib. ORCID 0009-0002-7162-7890. November 2026.

This is preprint v1 of the floor study. It records Part A as far as one bay, the reduced diaphragm, a joint strip, and gravity on that bay. There is no whole-building carbon result, and the search over geometries has not been run. The brief forbids that search until the validation rungs pass. There is no DOI.

## Question

A lighter floor cuts seismic mass, and it also cuts in-plane stiffness. The open question is where a vault bay stops acting as a rigid diaphragm. Hypothesis H1 says the flat plate is an upper bound on the in-plane stiffness of a curved ribbed floor of equal volume. Hypothesis H2 says the pass and the fail under EN 1998-1 4.3.1(4) fall on one diaphragm-to-frame ratio, alpha*, for every aspect ratio.

## What was calculated

The bay is 3 m square. The surface is z = f sin(π x / Lx) sin(π y / Ly), with rises 0.30 m and 0.60 m. The concrete in the floor cell is C30/37, E = 33 GPa and ν = 0.2. The mesh is a grid of CalculiX S8R shells. Equal volume means the faceted shell matches a flat plate 60 mm thick. One rib cross is a single element wide, 3/21 m, on a 50 mm shell, with the rib thickness set to that volume. The surface, the rises, the cross, the width and the 50 mm shell are still to be confirmed.

Stiffness is the plan membrane stiffness under three affine strains. Linear static, with no geometric stiffness. Et/(E T) divides by the 60 mm plate.

| Case | Et/(E T) | Gt/(G T) |
|---|---:|---:|
| Flat plate | 1.00000 | 1.00000 |
| Smooth, rise 0.30 m | 0.46875 | 0.65578 |
| Cross, rise 0.30 m | 0.43480 | 0.60185 |
| Diagonals, rise 0.30 m | 0.44408 | 0.65435 |
| Stress lines, rise 0.30 m, 0.375 m | 0.46328 | 0.64944 |
| Smooth, rise 0.60 m | 0.40763 | 0.46892 |
| Cross, rise 0.60 m | 0.38984 | 0.45189 |
| Diagonals, rise 0.60 m | 0.39834 | 0.47168 |
| Stress lines, 0.375 m | 0.40744 | 0.46840 |
| Stress lines, 0.75 m | 0.41394 | 0.46365 |

The flat, smooth and cross rows are `partE_validation/out/vault_rib.txt`, mesh 21×21. The rise 0.60 m diagonal row is `partB_generator/out/diagonal_bay.txt`, 41 elements, rib 104.77 mm, shell 50 mm. The rise 0.30 m diagonal row is `partB_generator/out/diagonal_rise030.txt`, 41 elements, rib 143.33 mm. At that rise the ratios are 0.02467 and 0.00143 below the smooth shell. The rise 0.30 m stress-line row is `partB_generator/out/stress_rib_rise030.txt`, spacing 0.375 m, 232 elements, rib 66.29 mm. Those ratios are 0.00547 and 0.00634 below the smooth shell. At rise 0.60 m the diagonal shear ratio is above the smooth shell. The 0.375 m row is `partB_generator/out/stress_rib.txt`, 236 elements, rib 59.16 mm. The 0.75 m row is `partB_generator/out/stress_rib_075.txt`, 128 elements, rib 66.65 mm. Both use a 50 mm shell. At rise 0.60 m the cross is 0.95637 of the smooth shell in extension and 0.96369 in shear. At 0.375 m the stress-line ratios are 0.00019 and 0.00052 below the smooth shell. At 0.75 m extension is 0.00631 above the smooth shell and shear is 0.00527 below it. H1 stays open. One cross, diagonals at two rises and these two spacings are not the ribbed floor.

The diaphragm ratio is alpha = K_d / K_f. K_d is the simply-supported Timoshenko stiffness of one bay, with the cell Et and Gt, and k = 5/6 as in the deep-beam check. K_f is the ground-storey stiffness of one anchor transverse frame: 1.174970×10⁸ N/m, height 4.55 m, beam inertia factor 2.0, C40 with E = 32.5 GPa and 600 mm columns, taken from the ShellBench anchor and not re-derived here. The author confirms the storey.

The floor model is that beam on a lateral spring at each frame line. The anchor spans are 6.0, 6.6, 6.6, 6.6, 6.6 and 6.0 m, and the depth is 21.0 m. A 3 m cell enters only through Et and Gt. The author confirms that step.

The pass test is the NOTE to EN 1998-1 4.3.1(4), read in the author's copy of BS EN 1998-1:2004, PDF page 55, printed page 53. The flexible displacement may exceed the rigid-diaphragm displacement by at most 10% of the absolute rigid displacement. The author confirms that sentence. Half of Et and Gt is reported beside the uncracked values, from 4.3.1(7), with K_f left as it is. The author confirms the half.

| Layout | L/D | alpha* |
|---|---:|---:|
| Seven equal bays | 0.300 | 54.651 |
| Seven equal bays | 0.500 | 97.479 |
| Seven equal bays | 1.000 | 247.188 |
| Seven equal bays | 2.000 | 495.420 |
| Anchor bays | 0.314 | 63.052 |

Two frames, and the definition of K_d, give 20. The beam element returns 19.9956. H2 is not supported on this model: alpha* moves with the aspect ratio. Source: `partE_validation/out/alpha_star.txt`.

On the anchor bays, uncracked, the displacement excess is 0.0509 for the flat plate, 0.1012 for the smooth rise of 0.60 m, and 0.1045 for the cross at that rise. With Et and Gt halved, those three become 0.0908, 0.1648 and 0.1692.

Gravity uses the same 21×21 mesh. Boundary translations are fixed and rotations are free. Density 2500 kg/m³. The author confirms the support and the density. No imperfection knockdown is applied.

| Case | Crown w, mm | Lowest positive factor on self-weight | Crown sxx, Pa |
|---|---:|---:|---|
| Flat, 60 mm | −0.7956 | 25122.1 | +5.701984×10⁵ and −5.701984×10⁵ |
| Smooth, rise 0.60 m | −0.0022 | 4933.37 | −1.941393×10⁴ and −1.684599×10⁴ |
| Cross, rise 0.60 m | −0.0024 | 5210.6 | −1.867630×10⁴ and −1.325382×10⁴ |
| Diagonals, rise 0.60 m | −0.0028 | 4272.83 | −1.478991×10⁴ and −1.460445×10⁴ |
| Smooth, rise 0.30 m | −0.006964 | 2319.99 | −5.014637×10⁴ and −2.806953×10⁴ |
| Cross, rise 0.30 m | −0.0095 | 2789 | −4.546519×10⁴ and −3.102803×10⁴ |
| Diagonals, rise 0.30 m | −0.0093 | 1856.27 | −3.709125×10⁴ and −2.155468×10⁴ |
| Stress lines, rise 0.30 m, 0.375 m | −0.0067 | 2405.68 | −5.470485×10⁴ and −2.852846×10⁴ |
| Stress lines, 0.375 m | −0.0022 | 5012.74 | −2.022574×10⁴ and −1.691824×10⁴ |
| Stress lines, 0.75 m | −0.0022 | 5383.24 | −1.962041×10⁴ and −1.705144×10⁴ |

The flat crown bends. The vault crown is in compression on both faces. Over the whole smooth rise of 0.60 m, 24 of 441 elements have one tensile membrane principal, all at the four corners. The largest is 6.950346×10³ Pa. Over the smooth rise of 0.30 m, 32 of 441 elements have one tensile principal. The farthest tensile centroid is 0.4165 m from a plan corner. The largest is 9.369478×10³ Pa. On the cross the counts are the same, 32 at rise 0.30 m and 24 at rise 0.60 m. The largest principals are 1.031277×10⁴ Pa and 7.047014×10³ Pa. The farthest tensile centroids are 0.4165 m and 0.3642 m from a plan corner. On the diagonals the count is 24 at both rises. The largest principals are 5.770915×10³ Pa and 5.506480×10³ Pa. The farthest tensile centroid is 0.3642 m from a plan corner. On the stress lines the count matches the smooth bay: 32 at rise 0.30 m and spacing 0.375 m, and 24 at rise 0.60 m for both spacings. The farthest tensile centroids are 0.4165 m and 0.3642 m from a plan corner. The largest principals are 1.020770×10⁴ Pa, 6.630235×10³ Pa and 6.193632×10³ Pa. The cross does not cut the crown deflection. The diagonals do not either. Their factor is 4272.83 at rise 0.60 m and 1856.27 at rise 0.30 m. The rise 0.30 m stress lines have factor 2405.68 and crown −0.0067 mm. The smooth crown in that print is −0.006964 mm. At that rise the smooth factor is 2319.99 and the cross factor is 2789, with cross crown −0.0095 mm. `gravity_bay.txt` has no rise 0.30 m row. The smooth and cross factors are `partE_validation/out/gravity_rise030.txt`. The smooth faces are the stress print. Both stress-line crowns match the smooth shell at −0.0022 mm. The factors are 5012.74 at 0.375 m and 5383.24 at 0.75 m. The first three rows are `partE_validation/out/gravity_bay.txt`. The diagonal rows are `partB_generator/out/diagonal_bay.txt` and `partB_generator/out/diagonal_rise030.txt`. The corner counts are `partB_generator/out/compression_smooth.txt`, `compression_smooth_rise030.txt`, `compression_cross_rise030.txt` and `compression_cross_rise060.txt`, `compression_diagonal_rise030.txt` and `compression_diagonal_rise060.txt`, `compression_stress_rise030_s375.txt`, `compression_stress_rise060_s375.txt` and `compression_stress_rise060_s750.txt`. The stress-line rows are `partB_generator/out/stress_rib.txt`, `stress_rib_075.txt` and `stress_rib_rise030.txt`.

A joint is a centreline strip whose modulus is the factor times E. Factor 1 is the continuous floor. At factor 0.1 the flat plate keeps 0.58615 of its extensional stiffness on a strip 0.333 m wide, and 0.68666 on a strip 0.200 m wide. The width is the element width. The author confirms the strip. Source: `partE_validation/out/joint_stiffness.txt`.

## Checks

| Check | Result |
|---|---|
| Rung 1, flat cell | PASS. Worst error 1.62×10⁻⁶ %, limit 1 % |
| Rung 2, deep beam | PASS. Worst error 0.21 %, limit 2 % |
| Rise zero on the smooth bay | PASS. Et 1.684×10⁻⁶ %, Gt 1.155×10⁻¹² %, limit 0.1 % |
| Rung 4, 3 m deep beam against its own Et, Gt | Flat −2.93 %, inside 5 %. Rise 0.60 m +15.80 %, outside 5 % |
| X-strut grid, calibrated on Et and Gt, checked on the deep beam | 1 m panel +9.83 %. 0.5 m panel +12.74 %. Both outside 5 % |

The 5 % figure is the brief's rung-4 limit. It is not a code clause. The Timoshenko reduction passes for the flat plate and does not pass for this vault. The X-strut does not pass for the flat plate either, and a finer panel does not close the gap.

## What this version does not show

There is no optimum shape and no saving in whole-building carbon. The generator reproduces this bay. The frame design loop and the search are not started. Rungs 3 and 5 stay in ShellBench until that loop exists. The diaphragm model is one linear storey on springs. Cracking, a topping and a tie are not in the run. One cross, diagonals at two rises, two stress-line spacings and one joint strip are not a segmented floor.
