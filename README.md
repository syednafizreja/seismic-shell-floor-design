# Seismic shell floors

In-plane stiffness of one vault bay, the diaphragm ratio of that stiffness on the anchor frame, and gravity on the same bay. The generator, the building loop and the search are not in this record.

[Key finding](#key-finding) | [Check it](#check-it-in-three-steps) | [Method](#method) | [Figures](#figures) | [Validation](#validation) | [Brief](brief.md) | [About](#about)

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/img/hero_dark.png">
  <img alt="Two bar charts on the same scale, bars starting at zero. Extensional ratio to a flat 60 mm plate: flat 1.00000, smooth rise 0.30 m 0.46875, cross 0.43480, smooth rise 0.60 m 0.40763, cross 0.38984. Shear ratio: 1.00000, 0.65578, 0.60185, 0.46892, 0.45189." src="docs/img/hero_light.png">
</picture>

| Rise 0.60 m, equal volume | Smooth shell | One rib cross | alpha* at L/D 0.3 | alpha* at L/D 2 |
|---|---:|---:|---:|---:|
| Et/(E T), and alpha* on seven equal bays | 0.40763 | 0.38984 | 54.651 | 495.420 |

## Key finding

*Question:* at equal concrete volume, how much of a flat plate's in-plane stiffness does one vault bay keep, and does one rib cross give any of it back? Hypothesis H1 in [brief.md](brief.md).

> One rib cross stays below the smooth shell. At rise 0.60 m, Et/(E T) is 0.38984 on the cross and 0.40763 on the smooth shell. The flat plate is 1.00000.

| Hypothesis | Verdict | Key numbers |
|---|---|---|
| H1. Flat-plate in-plane stiffness is an upper bound for the curved, ribbed floor of equal volume | Open. The smooth shell, the cross, the diagonals and both stress-line spacings are below the flat plate. The cross is below the smooth shell. None of these layouts closes H1 | Rise 0.30 m diagonals 0.44408 and 0.65435. Rise 0.60 m, 21×21: smooth 0.40763 and 0.46892; cross 0.38984 and 0.45189; diagonals 0.39834 and 0.47168; stress lines 0.375 m, 0.40744 and 0.46840; stress lines 0.75 m, 0.41394 and 0.46365 |

| Recorded | Not in this record |
|---|---|
| Rungs 1 and 2. Smooth bay. One rib cross. Diagonals at rise 0.30 m and 0.60 m. Principal-stress ribs at 0.375 m and 0.75 m. Corner tension on the smooth bay. A joint strip. Timoshenko K_d for the flat plate. alpha* on the anchor frame. Gravity on the 3 m bay | The X-strut within 5 %, the building loop, NSGA-II |

The figure is the equal-volume comparison, Et/(E T) and Gt/(G T), with T = 60 mm. [partE_validation/out/vault_rib.txt](partE_validation/out/vault_rib.txt). Plotted values: [docs/img/hero.json](docs/img/hero.json).

| Case | Mesh | t shell mm | t rib mm | Area/plan | Et/(E T) | Gt/(G T) | Et/(E t*) |
|---|---|---:|---:|---:|---:|---:|---:|
| Smooth, rise 0 | 21×21 | 60.0 | 60.0 | 1.0000 | 1.00000 | 1.00000 | 1.00000 |
| Cross, rise 0 | 21×21 | 50.0 | 157.6 | 1.0000 | 0.94989 | 0.89831 | |
| Smooth, rise 0.30 m | 21×21 | 58.6 | 58.6 | 1.0243 | 0.46875 | 0.65578 | 0.48013 |
| Cross, rise 0.30 m | 21×21 | 50.0 | 142.2 | 1.0243 | 0.43480 | 0.60185 | |
| Smooth, rise 0.60 m | 21×21 | 54.9 | 54.9 | 1.0931 | 0.40763 | 0.46892 | 0.44560 |
| Cross, rise 0.60 m | 21×21 | 50.0 | 102.5 | 1.0931 | 0.38984 | 0.45189 | |

At rise 0.60 m the cross is 0.95637 of the smooth shell in extension and 0.96369 in shear. At rise 0.30 m those ratios are 0.92757 and 0.91777. On the flat plate they are 0.94989 and 0.89831.

Two diagonals on the same rise and the same volume, shell 50 mm, rib 104.77 mm, 41 elements: Et/(E T) 0.39834 and Gt/(G T) 0.47168. [partB_generator/out/diagonal_bay.txt](partB_generator/out/diagonal_bay.txt). The generator reproduces the recorded smooth shell and the cross to 2.91e-06. [partB_generator/out/reproduce_bay.txt](partB_generator/out/reproduce_bay.txt). *Author to confirm the diagonals.*

At rise 0.30 m the same diagonals, 41 elements, rib 143.33 mm, give Et/(E T) 0.44408 and Gt/(G T) 0.65435. Those are 0.02467 and 0.00143 below the smooth shell at that rise, 0.46875 and 0.65578. [partB_generator/out/diagonal_rise030.txt](partB_generator/out/diagonal_rise030.txt). *Author to confirm the rise.*

Principal-stress ribs follow both families of the gravity membrane stress on that smooth bay. The spacing is 0.375 m. The strip is half an element pitch. 24 lines cover 236 of 441 elements, and the rib is 59.16 mm on a 50 mm shell. Et/(E T) 0.40744 and Gt/(G T) 0.46840, which are 0.00019 and 0.00052 below the smooth shell. [partB_generator/out/stress_rib.txt](partB_generator/out/stress_rib.txt). Doubling the spacing to 0.75 m leaves 12 lines, 128 elements and a rib of 66.65 mm. Et/(E T) 0.41394 is 0.00631 above the smooth shell, and Gt/(G T) 0.46365 is 0.00527 below it. [partB_generator/out/stress_rib_075.txt](partB_generator/out/stress_rib_075.txt). Both spacings stay under the flat plate. *Author to confirm the field, the axes and the spacings.*

The earlier mesh table uses another ratio. Et/(E t) there divides by the thickness in the row, not by 60 mm. For the 16×16 equal-volume row at rise 0.60 m, 0.44562 / 1.0930 = 0.40770, beside 0.40763 on the 21×21 mesh. [partE_validation/out/vault_bay.txt](partE_validation/out/vault_bay.txt).

<details>
<summary>Mesh record, including the 6×3 m bay</summary>

| Case | Mesh | t mm | Area/plan | Et/(E t) | Gt/(G t) |
|---|---|---:|---:|---:|---:|
| Square 3 m, rise 0 | 8×8 | 60.0 | 1.0000 | 1.00000 | 1.00000 |
| 3×3 m, rise 0.30 m, equal t | 8×8 | 60.0 | 1.0240 | 0.48155 | 0.67712 |
| 3×3 m, rise 0.30 m, equal t | 16×16 | 60.0 | 1.0242 | 0.48132 | 0.67614 |
| 3×3 m, rise 0.30 m, equal V | 16×16 | 58.6 | 1.0242 | 0.48014 | 0.67173 |
| 3×3 m, rise 0.60 m, equal t | 4×4 | 60.0 | 1.0886 | 0.45713 | 0.57026 |
| 3×3 m, rise 0.60 m, equal t | 8×8 | 60.0 | 1.0921 | 0.44789 | 0.52279 |
| 3×3 m, rise 0.60 m, equal V | 8×8 | 54.9 | 1.0921 | 0.44602 | 0.51455 |
| 3×3 m, rise 0.60 m, equal t | 12×12 | 60.0 | 1.0928 | 0.44758 | 0.52133 |
| 3×3 m, rise 0.60 m, equal t | 16×16 | 60.0 | 1.0930 | 0.44752 | 0.52114 |
| 3×3 m, rise 0.60 m, equal V | 16×16 | 54.9 | 1.0930 | 0.44562 | 0.51267 |
| 6×3 m, rise 0.60 m, equal t | 8×4 | 60.0 | 1.0565 | 0.82641 | 0.59070 |
| 6×3 m, rise 0.60 m, equal t | 16×8 | 60.0 | 1.0583 | 0.82359 | 0.57860 |
| 6×3 m, rise 0.60 m, equal V | 16×8 | 56.7 | 1.0583 | 0.82164 | 0.57224 |

Rise zero against the flat cell in the same file: Et 1.684e-06 %, Gt 1.155e-12 %. The limit is 0.1 %.

| Mesh change, equal thickness | Et/(E t) | Gt/(G t) |
|---|---|---|
| 3 m, rise 0.30 m, 8×8 to 16×16 | 0.48155 to 0.48132 | 0.67712 to 0.67614 |
| 3 m, rise 0.60 m, 12×12 to 16×16 | 0.44758 to 0.44752 | 0.52133 to 0.52114 |
| 6×3 m, rise 0.60 m, 8×4 to 16×8 | 0.82641 to 0.82359 | 0.59070 to 0.57860 |

The 6×3 m shear ratio still moves between those two meshes. The long direction of that bay is flatter than the square at the same rise, and its equal-volume Et/(E t) is 0.82164.

</details>

| Limit | Record |
|---|---|
| Surface | z = f sin(π x / Lx) sin(π y / Ly). *Author to confirm the surface and the rises 0.30 m and 0.60 m.* |
| Ribs | One cross on the centreline. Width 3/21 m. Shell 50 mm. Rib thickness set to the 60 mm volume. *Author to confirm the cross, the width and the 50 mm shell.* |
| Comparison | Et/(E T) and Gt/(G T), T = 60 mm. The mesh table also prints Et/(E t) of the row thickness |
| Analysis | Linear static S8R for the cell. Gravity adds self-weight and a linear buckling factor. No imperfection knockdown |
| Area | Faceted corner triangles over the plan. The mid-side curve is not counted |

> H2 is not supported on this model. alpha* of seven equal bays is 54.651 at L/D 0.3 and 495.420 at L/D 2. On the anchor bays the uncracked excess at rise 0.60 m is 0.1012 (smooth) and 0.1045 (cross). The 10 % line is the NOTE to EN 1998-1 4.3.1(4), author's copy.

| Layout | L/D | alpha* |
|---|---:|---:|
| Seven equal bays | 0.300 | 54.651 |
| Seven equal bays | 0.500 | 97.479 |
| Seven equal bays | 1.000 | 247.188 |
| Seven equal bays | 2.000 | 495.420 |
| Anchor bays | 0.314 | 63.052 |

| Cell on the anchor bays | Et/(E T) | Gt/(G T) | alpha | Uncracked excess | Half Et, Gt: alpha | Half: excess |
|---|---:|---:|---:|---:|---:|---:|
| Smooth, rise 0 | 1.00000 | 1.00000 | 142.82 | 0.0509 | 71.41 | 0.0908 |
| Cross, rise 0 | 0.94989 | 0.89831 | 128.58 | 0.0545 | 64.29 | 0.0965 |
| Smooth, rise 0.30 m | 0.46875 | 0.65578 | 92.15 | 0.0854 | 46.07 | 0.1417 |
| Cross, rise 0.30 m | 0.43480 | 0.60185 | 84.62 | 0.0908 | 42.31 | 0.1494 |
| Smooth, rise 0.60 m | 0.40763 | 0.46892 | 66.56 | 0.1012 | 33.28 | 0.1648 |
| Cross, rise 0.60 m | 0.38984 | 0.45189 | 64.12 | 0.1045 | 32.06 | 0.1692 |

K_f of the ground storey, beam inertia factor 2.0, is 1.174970×10⁸ N/m. Two frames give alpha* 19.9956, against 20 from the definition of K_d. The beam element is −0.003 % from the closed deflection. [partE_validation/out/alpha_star.txt](partE_validation/out/alpha_star.txt). The half is 4.3.1(7). *Author to confirm the clause, the storey, and the half.*

| Gravity, 21×21, pinned boundary | Crown w, mm | Lowest positive factor | Crown sxx, Pa |
|---|---:|---:|---|
| Flat, 60 mm | −0.7956 | 25122.1 | +5.701984×10⁵ and −5.701984×10⁵ |
| Smooth, rise 0.60 m | −0.0022 | 4933.37 | −1.941393×10⁴ and −1.684599×10⁴ |
| Cross, rise 0.60 m | −0.0024 | 5210.6 | −1.867630×10⁴ and −1.325382×10⁴ |
| Diagonals, rise 0.60 m | −0.0028 | 4272.83 | −1.478991×10⁴ and −1.460445×10⁴ |
| Diagonals, rise 0.30 m | −0.0093 | 1856.27 | −3.709125×10⁴ and −2.155468×10⁴ |
| Stress lines, 0.375 m | −0.0022 | 5012.74 | −2.022574×10⁴ and −1.691824×10⁴ |
| Stress lines, 0.75 m | −0.0022 | 5383.24 | −1.962041×10⁴ and −1.705144×10⁴ |

The first three rows are [partE_validation/out/gravity_bay.txt](partE_validation/out/gravity_bay.txt). That file has no rise 0.30 m row. The diagonal rows are [partB_generator/out/diagonal_bay.txt](partB_generator/out/diagonal_bay.txt) and [diagonal_rise030.txt](partB_generator/out/diagonal_rise030.txt). The stress-line rows are [partB_generator/out/stress_rib.txt](partB_generator/out/stress_rib.txt) and [stress_rib_075.txt](partB_generator/out/stress_rib_075.txt). On the smooth rise of 0.60 m, 24 of 441 elements have one tensile membrane principal, all at the four corners. The largest is 6.950346×10³ Pa. [partB_generator/out/compression_smooth.txt](partB_generator/out/compression_smooth.txt). Rotations on the boundary are free. Density 2500 kg/m³. No knockdown. *Author to confirm the support, the density and the tension check.*

| Joint factor 0.1, flat 60 mm | Strip width | Et / continuous |
|---|---:|---:|
| 9×9 | 0.333 m | 0.58615 |
| 15×15 | 0.200 m | 0.68666 |

Factor 1 is the continuous floor. [partE_validation/out/joint_stiffness.txt](partE_validation/out/joint_stiffness.txt). *Author to confirm the strip.*

## Check it in three steps

The `research` conda env is shared. `cecore` comes from `ComputationalEngineering/cecore` and is not inside this repository. CalculiX 2.23 is required for the three record scripts. On PowerShell, set `$env:PYTHONPATH = "."` before each script.

**1. Environment**

```bash
conda activate research
```

**2. Record** (from this folder)

```bash
PYTHONPATH=. python partE_validation/rung1_unit_cell.py
PYTHONPATH=. python partE_validation/rung2_deep_beam.py
PYTHONPATH=. python partE_validation/vault_bay.py
PYTHONPATH=. python partE_validation/vault_rib.py
PYTHONPATH=. python partE_validation/joint_stiffness.py
PYTHONPATH=. python partE_validation/xstrut_check.py
PYTHONPATH=. python partE_validation/rung4_storey.py
PYTHONPATH=. python partE_validation/gravity_bay.py
PYTHONPATH=. python partE_validation/alpha_star.py
```

`alpha_star.py` imports the ShellBench anchor frame and OpenSees. The number it prints for K_f is the one in the table above.

**3. Figures**

```bash
python scripts/readme_hero.py
python scripts/alpha_fig.py
```

Outputs: `partE_validation/out/`. The hero numbers: `docs/img/hero.json`.

## Method

$$
z = f \sin(\pi x / L_x)\sin(\pi y / L_y)
$$

$$
t^{*} = t\,\frac{L_x L_y}{A_{\text{faceted}}}
\qquad
(Et)_{\text{eq}} = A_{00} - A_{01}^{2}/A_{11}
\qquad
(Gt)_{\text{eq}} = A_{22}
$$

| Item | Value |
|---|---|
| Plan | 3 × 3 m, and one 6 × 3 m bay. The 3 m cell is the rung-1 plan |
| Material | C30/37, E = 33 GPa, ν = 0.2, reference thickness 60 mm |
| Mesh | Structured S8R, the rung-1 grid lifted onto the surface. Gmsh is not used |
| Boundary | Affine u and v, and w = 0, on the plan boundary only. Interior nodes are free |
| Strain | Three states, magnitude 1×10⁻⁴. Resultants from the virtual work of the plan reactions, divided by the plan area |
| Equal volume | t* above, so the faceted surface matches the 60 mm plate. Equal thickness is reported beside it |
| Ribs | Orthogonal cross, one element wide, on the 21×21 mesh. Two shell sections |
| Code | [partA_mechanics/plate_fe.py](partA_mechanics/plate_fe.py), `shell_membrane_stiffness` |

A rise of zero uses the same grid as `membrane_stiffness` and must agree within 0.1 %. Curved rows have no pass mark. They are the record.

## Figures

Drawn from `partE_validation/out/vault_rib.txt` by [scripts/readme_hero.py](scripts/readme_hero.py). The number on the figure is the file value.

| Equal-volume stiffness | |
|---|---|
| <img src="docs/img/hero_light.png" alt="Extensional and shear stiffness of the flat plate, the smooth bay and one rib cross, divided by a flat 60 mm plate. Bars start at zero." width="720"> | |
| Equal-volume rows of the smooth shell and one rib cross. Source: `partE_validation/out/vault_rib.txt`. | |

| alpha* | |
|---|---|
| <img src="docs/img/alpha_light.png" alt="Left: alpha-star of seven equal bays is 54.651, 97.479, 247.188 and 495.420 at L/D 0.3, 0.5, 1 and 2. Right: uncracked displacement excess, with the rise 0.60 m bars at 0.1012 and 0.1045 above the 0.10 line." width="720"> | |
| Drawn by `scripts/alpha_fig.py` from `partE_validation/out/alpha_star.txt`. | |

## Validation

| Check | Limit | Result | File |
|---|---|---|---|
| Rung 1. Flat cell against exact E t, G t | 1 % | PASS. Worst error 1.62e-06 % | [partE_validation/out/rung1_unit_cell.txt](partE_validation/out/rung1_unit_cell.txt) |
| Rung 2. Deep beam against Timoshenko | 2 % | PASS. Worst error 0.21 %. Shear share 3.5 % to 36.5 % | [partE_validation/out/rung2_deep_beam.txt](partE_validation/out/rung2_deep_beam.txt) |
| Rise zero against the flat cell | 0.1 % | PASS. Et 1.684e-06 %, Gt 1.155e-12 % | [partE_validation/out/vault_bay.txt](partE_validation/out/vault_bay.txt) |
| Smooth rise 0 on the rib mesh | exact E T | 1.00000 and 1.00000. The cross has no pass mark | [partE_validation/out/vault_rib.txt](partE_validation/out/vault_rib.txt) |
| Rung 4. Shell deep beam against its own Et, Gt, 3 m bay | 5 % | Flat −2.93 %, pass. Rise 0.60 m +15.80 %, fail | [partE_validation/out/rung4_storey.txt](partE_validation/out/rung4_storey.txt) |
| X-strut, calibrated on Et and Gt, checked on the 12 m deep beam | 5 % | 1 m panel +9.83 %. 0.5 m panel +12.74 %. Both fail | [partE_validation/out/xstrut_check.txt](partE_validation/out/xstrut_check.txt) |
| Two-frame alpha* | 20, from the definition of K_d | 19.9956. Beam element −0.003 % | [partE_validation/out/alpha_star.txt](partE_validation/out/alpha_star.txt) |

Rungs 3 and 5 already exist in ShellBench. They are rerun when Part C is wired. ShellBench is imported, not edited.

## Where to find things

| You want | Look in |
|---|---|
| The question and H1 | [brief.md](brief.md) |
| Choices still to confirm | [docs/decisions.md](docs/decisions.md) |
| The smooth-bay mesh record | [partE_validation/out/vault_bay.txt](partE_validation/out/vault_bay.txt) |
| The rib cross | [partE_validation/out/vault_rib.txt](partE_validation/out/vault_rib.txt) |
| Two diagonals, and the generator check | [partB_generator/out/diagonal_bay.txt](partB_generator/out/diagonal_bay.txt), [diagonal_rise030.txt](partB_generator/out/diagonal_rise030.txt), [reproduce_bay.txt](partB_generator/out/reproduce_bay.txt) |
| Corner tension on the smooth bay | [partB_generator/out/compression_smooth.txt](partB_generator/out/compression_smooth.txt) |
| Principal-stress ribs | [partB_generator/out/stress_rib.txt](partB_generator/out/stress_rib.txt), [stress_rib_075.txt](partB_generator/out/stress_rib_075.txt) |
| alpha*, the joint strip, gravity | [partE_validation/out/alpha_star.txt](partE_validation/out/alpha_star.txt), [joint_stiffness.txt](partE_validation/out/joint_stiffness.txt), [gravity_bay.txt](partE_validation/out/gravity_bay.txt) |
| Preprint v1 | [docs/preprint_v1.md](docs/preprint_v1.md) |
| The solver | [partA_mechanics/plate_fe.py](partA_mechanics/plate_fe.py), [reduced.py](partA_mechanics/reduced.py) |
| The figure scripts | [scripts/readme_hero.py](scripts/readme_hero.py), [scripts/alpha_fig.py](scripts/alpha_fig.py) |

| Folder | Brief part | State |
|---|---|---|
| `partA_mechanics/` | Unit cell, vault bay, reduced diaphragm | Solver, Timoshenko K_d, X-strut grid |
| `partB_generator/` | Floor generator | Reproduces the recorded bay. Diagonals at 0.30 m and 0.60 m, and stress-line ribs at 0.375 m and 0.75 m, are in the record |
| `partC_building/` | Whole building | Not started |
| `partD_optimise/` | NSGA-II | Not started. The brief forbids it before the rungs pass |
| `partE_validation/` | Rungs 1–8 | Rungs 1, 2 and the deflection half of 4. Joint strip, gravity, alpha* |

## Citation

There is no archived release and no DOI. Cite the code and the record as:

```bibtex
@software{hasib2026shellfloors,
  author = {Hasib, Syed Nafiz Reja},
  title  = {One vault bay: in-plane stiffness, a diaphragm ratio, and gravity},
  year   = {2026},
  url    = {https://github.com/syednafizreja/seismic-shell-floor-design}
}
```

## About

Syed Nafiz Reja Hasib, civil and structural engineer. [ORCID 0009-0002-7162-7890](https://orcid.org/0009-0002-7162-7890).

This repository is the record of one vault bay: its in-plane stiffness, a diaphragm ratio on the anchor spans, and gravity on that bay. There is no carbon optimum and no search. The question is fixed in [brief.md](brief.md). Every number above is taken from a file named beside it.

The public page states the same record and does not link this repository: [seismic shell floors](https://syednafizreja.github.io/work/seismic-shell-floors/).

## Licence

Code: MIT ([LICENSE](LICENSE)).
