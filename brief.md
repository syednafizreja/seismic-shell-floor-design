# Project 1 (v3): Light enough, stiff enough

Seismic-aware computational design of low-carbon shell floors for RC buildings

Status: v3, 10 Nov 2026. Replaces v1 and v2. Nothing from v2 is dropped; v2 becomes Part A.
(Saved to disk 17 Nov 2026 from the author's brief, text unchanged.)

## 1. Why v3
v2 answered the mechanics committees (STRAINS, MS2, GeM) but gave the US list almost nothing, and it was analysis, not design. Your energy comes from design: geometry, form, exploring options, building the tool. Every person on your US list works on design optimisation of efficient concrete (Mueller, Carstensen, Jewett, Paulino, Zhang). So v3 keeps all of v2's mechanics and puts it inside a design engine.

## 2. The gap (checked 10 Nov 2026)
Shape- and topology-optimised concrete floors are an active field, and all of it is driven by gravity:
- Ismail & Mueller 2021, Eng. Struct. 246: shaped one-way floors, 48-64% less embodied energy, gravity design.
- Amir & Majdouba 2024, SMO 67(6): ribbed-plate topology/shape/sizing optimisation, 24-57% lighter, gravity.
- Whiteley, Liew, He et al. 2023, Structures: optimised RC floor grillages, 40-50% savings, gravity.
- Oval et al. 2023, Structures: segmented shell floor prototype, about 50% less A1-A3 carbon.
- Ranaudo et al. 2021 (ETH HiLo): rib-stiffened funicular floor, up to 70% less concrete.
- Feickert & Mueller 2023: lighter floors + shell foundations give whole-building downstream savings, but no seismic loads.
- Jewett & Carstensen 2026 (arXiv 2604.22070): topology-optimised RC beams, built and tested.
Closest work with horizontal loads: Chiang & Borgart 2021 (membrane shells carrying horizontal load need perimeter walls) and Terazawa et al. 2022 (response-spectrum morphogenesis of gridshell roofs). Neither looks at a floor acting as a diaphragm in a multi-storey frame.

What nobody has done: design the floor shape for the earthquake case, where the floor has to carry lateral shear in its own plane, and count the carbon of the whole building, not only the floor.

Caveat: the database search came back thin, which can mean the search words were wrong rather than that the gap is open. Phase 0 reruns it in Scopus/Web of Science vocabulary before anything is claimed.

## 3. The research question
A lighter floor cuts seismic mass, so columns, beams and foundations get smaller. A lighter floor also has less in-plane stiffness, so past some point it stops acting as a rigid diaphragm, and topping or ties put carbon back. Where is the best trade-off, and what floor geometry reaches it?

RQ1 (mechanics): What in-plane stiffness does a rib-stiffened funicular floor have, and at what diaphragm-to-frame stiffness ratio alpha does it fail EN 1998-1 4.3.1(4)?
RQ2 (design): Which floor geometries (rise, shell thickness, rib layout, rib depth, topping) minimise whole-building A1-A3 carbon while passing gravity, diaphragm and drift checks?
RQ3 (insight): Does designing for gravity alone give a floor that is close to the seismic-aware optimum, or does the earthquake case change the shape? This is the headline result either way.

Pre-registered hypotheses
- H1: flat-plate in-plane stiffness is an upper bound for the curved, ribbed floor of equal volume.
- H2: pass and fail under EC8 collapse onto one threshold alpha* across aspect ratios.
- H3: at 0.10g the gravity-only optimum is near-optimal; at 0.20-0.40g the seismic-aware optimum is a different geometry (more rise or diagonal ribs), with a measurable carbon gap.
- H4: whole-building savings exceed floor-only savings because of the mass feedback, but by less than gravity-only studies imply.

## 4. Architecture (five parts, all kept)

Part A: Mechanics core (v2, unchanged)
- Unit-cell homogenisation of one vault bay (CalculiX shells + Gmsh): uniform in-plane strains give (E t)_eq and (G t)_eq.
- Reduced diaphragm model: equivalent orthotropic membrane, with a calibrated X-strut grid as the fast option.
- Timoshenko deep-beam stiffness K_d against frame stiffness K_f gives alpha = K_d / K_f. The same formula is both the benchmark and the design rule.
- Segmented floors: joint-stiffness factor 1.0 to 0.1.

Part B: Floor design generator (the creative part)
- Form-finding: force-density (ShellBench code) for the vault surface.
- Design variables: rise/span, shell thickness, rib layout family (orthogonal, diagonal, principal-stress trajectory; the trajectory tracer is shared with Project 2), rib depth, topping thickness, edge-tie area.
- Gravity checks per candidate: shell FE stresses, compression-only check, deflection limits, linear buckling with an imperfection knockdown factor.
- Constructability measure: number of unique segments and formwork area, after Wehner & Ismail 2025.

Part C: Whole-building loop
- ShellBench's design generator resizes beams and columns to GB 50011 and EC8 for each floor's mass.
- Response spectrum analysis (GB 50011 and EC8 Type 1), EC8 diaphragm rule, drift limits, capacity design.
- Whole-building A1-A3 carbon (floor + ties + topping + beams + columns + foundations), ICE v3 and GB/T 51366 factors, ±30% sensitivity.
- Seismic levels: 0.05-0.40g, as in ShellBench.

Part D: Optimisation and design-space exploration
- NSGA-II (pymoo), three objectives: whole-building carbon, diaphragm margin (alpha/alpha*), constructability.
- Baseline run: the same optimiser with gravity checks only, to answer RQ3.
- ML surrogate (ShellBench Paper 2 merged in here, where it has a real job): trained on full-model runs, used to pre-screen candidates, with every Pareto point re-checked by the full model.
- Interactive explorer (three.js, like the canopy tool): move along the Pareto front and watch the floor shape, the building's member sizes and the carbon change together.

Part E: Validation ladder (every rung reported with its error)
1. Flat-plate unit cell vs exact E t and G t: under 1%.
2. Flat deep-beam floor vs Timoshenko: under 2%.
3. Scordelis-Lo roof and pinched hemisphere (already in ShellBench).
4. One storey with reduced model vs full shell model: deflection and first period within 5%.
5. Rigid-diaphragm frame vs thesis hand calculations (already in ShellBench).
6. Optimiser check: on a 2-variable slice, NSGA-II front vs brute-force grid.
7. Surrogate: held-out error reported; no Pareto claim rests on the surrogate alone.
8. Sanity range: optimised floor carbon vs published HiLo (about 30 kgCO2e/m2 for a 5.2 m span) and Oval 2023.

## 5. What each target sees

| Target | What they look for | Where it is |
|---|---|---|
| Mueller (MIT) | Design-space exploration, shaped floors, carbon, interactive tools | Parts B, D, explorer; extends Ismail & Mueller 2021 to seismic |
| Carstensen (MIT), Jewett (Northwestern) | Optimised RC for low carbon, buildable | Parts D, B constructability; the lateral load case their floor work leaves out |
| Paulino, Zhang (UIUC) | Optimisation formulation, multiple load cases | Part D: gravity + seismic as competing load cases |
| Mesnil, Douthe, Oval (Navier) | Shells, rib patterns, segmented floors | Parts A (joint stiffness), B (rib layouts) |
| Kotronis (GeM), MS2 | Seismic dynamics, simplified models | Part A reduced model, Part C |
| STRAINS | Solid mechanics depth | Part A homogenisation, Timoshenko, shell buckling |
| ETH Block / Empa (long term) | Funicular floors in real buildings | RQ3 result |

One story across all of them: computational design of efficient shell systems under seismic loading, with carbon as a design variable.

## 6. How it connects to your other streams
- ShellBench Paper 1 (whole-building carbon of shell floors, rigid diaphragm): stays as it is. Project 1 removes its main assumption and turns analysis into design.
- ShellBench Paper 2 (ML surrogate): merged into Part D. Update CV item [7] when it is done.
- Project 2 (stress-trajectory ribs under lateral sway): stays a separate paper; shares the rib-layout module.
- ShellForm: unchanged.

## 7. Releases, timed to deadlines
Compute is not the limit; overnight runs are fine. The order is fixed: no optimisation before the validation rungs pass.

- Phase 0 (14-20 Nov, around IELTS): Scopus/WoS gap rerun; read the 8 key papers; freeze the hypotheses.
- Release 1 (by 15 Dec): Part A complete + gravity checks + first alpha* figure + preprint v1. Used in US emails and the US statement update (most US committees read files in Jan-Feb, so a short update email with the preprint in early Jan is normal).
- Release 2 (by 25 Jan): Parts B + C, gravity-only vs seismic-aware fronts at 0.10g and 0.30g, explorer v1. Goes into the STRAINS letter (3 Feb) and GeM/Navier emails.
- Release 3 (by 10 Mar): full Part D with surrogate, full validation ladder, preprint v2. Goes to MS2 (15 Mar), NORISK interviews, and the journal.

Journal: Engineering Structures (Elsevier, JCR Q1, IF 6.4; the subscription route has no fee; Ismail & Mueller 2021 is there). Fallback: Structures (JCR 2024 Q1 Civil). Conference: IASS 2027 symposium abstract, where Mueller and the Navier group publish [check the date].

## 8. Integrity rules for this project
- CV and letters say only what is done at that date. "Submission planned Nov 2026" lines change to the true status.
- Every number in a letter traces to a tagged release.
- Disclose AI-assisted coding, as the CV already does.
- No Denco material anywhere.

## 9. Honest limits (they go in the paper)
- Linear elastic diaphragm with EC8 cracked stiffness; diaphragm cracking and pushover are future work.
- One building typology (thesis frame family); regular plus one irregular variant.
- Form-found floors, not a built HiLo or Navier geometry; checked against published carbon only.

## Key references (read in Phase 0)
Ismail & Mueller 2021 (doi:10.1016/j.engstruct.2021.112955); Amir & Majdouba 2024 (doi:10.1007/s00158-024-03824-9); Whiteley et al. 2023 (doi:10.1016/j.istruc.2023.03.116); Oval et al. 2023 (doi:10.1016/j.istruc.2023.01.063); Feickert & Mueller 2023 (doi:10.1007/s44150-023-00101-z); Chiang & Borgart 2021 (doi:10.1016/j.engstruct.2021.113514); Jewett & Carstensen 2026 (arXiv:2604.22070); Kotronis & Grange 2010 (EJECE 14(6-7)); Micelli et al. 2014 (equivalent diaphragms); EN 1998-1 4.3.1.
