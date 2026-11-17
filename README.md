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
