# Project 1 (v3): Light enough, stiff enough

Brief: `brief.md`. Status: `../STATUS.md`. Local only: no GitHub remote until the author decides to release.

| Folder | Brief part |
|---|---|
| `phase0/` | gap rerun (Scopus/WoS search strings), reading list, hypothesis freeze |
| `partA_mechanics/` | unit-cell homogenisation, reduced diaphragm model, alpha = K_d/K_f (starts from `shellbench.diaphragm`) |
| `partB_generator/` | floor design generator; rib "trajectory" family imports the tracer from `../cecore` |
| `partC_building/` | whole-building loop, imports ShellBench's generator (`shellbench.generator`, `rsa`, `carbon`) |
| `partD_optimise/` | NSGA-II (`pymoo`), gravity-only baseline, surrogate |
| `partE_validation/` | validation ladder, rungs 1-8 |
| `explorer/` | three.js Pareto explorer |

Rule from the brief: no optimisation before the validation rungs pass.
ShellBench is imported, never edited from here (it is public and Zenodo-synced).

## Status (17 Nov 2026)

| Rung (brief Part E) | Script | Result |
|---|---|---|
| 1. Flat-plate unit cell vs exact E t, G t (limit 1 %) | `partE_validation/rung1_unit_cell.py` | PASS: worst error 2e-6 % over square and 2:1 cells, two meshes. This is a patch test of the homogenisation (affine boundary strains, reactions by virtual work); the vault-bay cells are the next step. |
| 2. Flat deep-beam floor vs Timoshenko (limit 2 %) | `partE_validation/rung2_deep_beam.py` | PASS: worst error 0.21 % for L/D = 2 to 8 on two meshes; shear carries 3.5 to 36.5 % of the deflection, so the shear term is tested. |
| 3-8 | not started | Rungs 3 and 5 exist in ShellBench and are rerun when Part C is wired in. |

Run from this folder: `PYTHONPATH=. python partE_validation/rung1_unit_cell.py` (Windows: same, the path has one entry). Outputs in `partE_validation/out/`.
Parts B-D (generator, building loop, optimisation) are not started; by the brief's rule, no optimisation before the rungs pass.
