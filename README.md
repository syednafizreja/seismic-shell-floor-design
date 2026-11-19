# Seismic shell floors

In-plane stiffness of one smooth concrete vault bay, set against a flat plate of equal volume. Ribs, the building model, and the search are not in this record.

[Key finding](#key-finding) | [Check it](#check-it-in-three-steps) | [Method](#method) | [Figures](#figures) | [Validation](#validation) | [Brief](brief.md) | [Cite](#citation)

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/img/hero_dark.png">
  <img alt="Two bar charts on the same scale, bars starting at zero. Extensional ratio to a flat plate: rise 0 is 1.00000, 3 m at rise 0.30 m is 0.48014, 3 m at rise 0.60 m is 0.44562, 6 by 3 m at rise 0.60 m is 0.82164. Shear ratio: 1.00000, 0.67173, 0.51267, 0.57224. A dashed line marks the flat plate." src="docs/img/hero_light.png">
</picture>

## Key finding

*Question:* at equal concrete volume, how much of a flat plate's in-plane stiffness does one smooth vault bay keep? Hypothesis H1 in [brief.md](brief.md) asks this of a curved, ribbed floor. This bay has no ribs.

> The smooth 3 m bay at rise 0.60 m, equal volume, keeps 0.44562 of the flat extensional stiffness and 0.51267 of the flat shear stiffness (16×16, t = 54.9 mm).

| Hypothesis | Verdict | Key numbers |
|---|---|---|
| H1. Flat-plate in-plane stiffness is an upper bound for the curved, ribbed floor of equal volume | Open. The smooth bay is below the flat plate. Ribs are not in this bay | 0.44562 and 0.51267 at rise 0.60 m, equal volume, 16×16 |

| Recorded | Not in this record |
|---|---|
| Rungs 1 and 2. One smooth sinusoidal bay, linear plan stiffness | Ribs, joints, reduced diaphragm, generator, building loop, NSGA-II |

The figure uses the rise-zero row and the finest equal-volume row of each curved bay. The full mesh table is below. Both are [partE_validation/out/vault_bay.txt](partE_validation/out/vault_bay.txt). Plotted values: [docs/img/hero.json](docs/img/hero.json).

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

The 6×3 m shear ratio still moves between those two meshes. The long direction of that bay is flatter than the square at the same rise, and it keeps more extensional stiffness (0.82164 at equal volume).

| Limit | Record |
|---|---|
| Surface | z = f sin(π x / Lx) sin(π y / Ly). *Author to confirm the surface and the rises 0.30 m and 0.60 m.* |
| Comparison | Et/(E t) and Gt/(G t) of a flat plate with the thickness in the row |
| Analysis | Linear static S8R. No geometric stiffness. No ribs |
| Area | Faceted corner triangles over the plan. The mid-side curve is not counted |

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
```

**3. Figure at the top**

```bash
python scripts/readme_hero.py
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
| Code | [partA_mechanics/plate_fe.py](partA_mechanics/plate_fe.py), `shell_membrane_stiffness` |

A rise of zero uses the same grid as `membrane_stiffness` and must agree within 0.1 %. Curved rows have no pass mark. They are the record.

## Figures

Drawn from `partE_validation/out/vault_bay.txt` by [scripts/readme_hero.py](scripts/readme_hero.py). The number on the figure is the file value.

| Equal-volume stiffness | |
|---|---|
| <img src="docs/img/hero_light.png" alt="Extensional and shear stiffness ratios for the flat bay and three equal-volume vaults. Bars start at zero." width="720"> | |
| Rise-zero row and the finest equal-volume row of each curved bay. Source: `partE_validation/out/vault_bay.txt`. | |

## Validation

| Check | Limit | Result | File |
|---|---|---|---|
| Rung 1. Flat cell against exact E t, G t | 1 % | PASS. Worst error 1.62e-06 % | [partE_validation/out/rung1_unit_cell.txt](partE_validation/out/rung1_unit_cell.txt) |
| Rung 2. Deep beam against Timoshenko | 2 % | PASS. Worst error 0.21 %. Shear share 3.5 % to 36.5 % | [partE_validation/out/rung2_deep_beam.txt](partE_validation/out/rung2_deep_beam.txt) |
| Rise zero against the flat cell | 0.1 % | PASS. Et 1.684e-06 %, Gt 1.155e-12 % | [partE_validation/out/vault_bay.txt](partE_validation/out/vault_bay.txt) |

Rungs 3 and 5 already exist in ShellBench. They are rerun when Part C is wired. ShellBench is imported, not edited.

## Where to find things

| You want | Look in |
|---|---|
| The question and H1 | [brief.md](brief.md) |
| Choices still to confirm | [docs/decisions.md](docs/decisions.md) |
| The vault-bay record | [partE_validation/out/vault_bay.txt](partE_validation/out/vault_bay.txt) |
| The solver | [partA_mechanics/plate_fe.py](partA_mechanics/plate_fe.py) |
| The figure script | [scripts/readme_hero.py](scripts/readme_hero.py) |

| Folder | Brief part | State |
|---|---|---|
| `partA_mechanics/` | Unit cell, then the smooth bay | Solver and the bay above |
| `partB_generator/` | Floor generator | Not started |
| `partC_building/` | Whole building | Not started |
| `partD_optimise/` | NSGA-II | Not started. The brief forbids it before the rungs pass |
| `partE_validation/` | Rungs 1–8 | Rungs 1 and 2, and the smooth bay |

## Citation

There is no archived release and no DOI. Cite the code and the record as:

```bibtex
@software{hasib2026shellfloors,
  author = {Hasib, Syed Nafiz Reja},
  title  = {In-plane stiffness of one smooth concrete vault bay against a flat plate of equal volume},
  year   = {2026},
  url    = {https://github.com/syednafizreja/seismic-shell-floor-design}
}
```

## Author and licence

Syed Nafiz Reja Hasib · [ORCID 0009-0002-7162-7890](https://orcid.org/0009-0002-7162-7890) · Code: MIT ([LICENSE](LICENSE))
