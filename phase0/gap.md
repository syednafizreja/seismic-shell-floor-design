# Gap search, 20 Nov 2026

The brief asks for a Scopus and Web of Science rerun before the gap sentence is claimed. This session had no institutional login. The database used was OpenAlex. *Author to confirm the same search in Scopus and Web of Science.*

## Question

Has a published study designed the geometry of a concrete shell or ribbed floor so that the floor carries in-plane seismic shear as a diaphragm in a multi-storey frame?

A further hit would also report the carbon of the whole building.

A paper counts only if it does all of the following:

- The floor is concrete.
- The geometry is designed: rise, ribs, thickness, topology, or a form-found shape. A choice among catalogue slabs does not count.
- The design load includes in-plane seismic shear, or an earthquake diaphragm check.
- The building is a multi-storey frame.

Gravity-only floors, roof gridshells, masonry vaults, steel decks, and a rigid diaphragm that is assumed rather than designed are recorded as neighbours. They do not meet the rule.

## Queries

OpenAlex works search, 20 Nov 2026. Counts are `meta.count` from that API.

| Tag | Query | Count |
|---|---|---|
| Q1 | search: shell floor diaphragm seismic | 2057 |
| Q2 | search: funicular floor earthquake diaphragm | 15 |
| Q3 | search: ribbed concrete floor diaphragm seismic optimisation | 25 |
| Q4 | search: vaulted slab in-plane stiffness seismic diaphragm | 99 |
| Q5 | search: concrete shell floor Eurocode 8 diaphragm | 742 |
| Q6 | title and abstract: diaphragm, seismic, and "shell floor" | 0 |
| Q7 | title and abstract: diaphragm, seismic, and funicular | 0 |
| Q8 | title and abstract: "ribbed floor", seismic, and diaphragm | 0 |
| F1 | title and abstract: seismic, "topology optimization", and floor | 8 |
| F2 | title and abstract: seismic, "shape optimization", and slab | 1 |
| F3 | title and abstract: "embodied carbon", diaphragm, and concrete | 5 |
| F4 | title and abstract: waffle, seismic, and slab | 75 |
| F5 | title and abstract: "shell floor" and seismic | 2 |
| F6 | title and abstract: funicular, floor, and seismic | 1 |
| F7 | title and abstract: "in-plane", "ribbed slab", and seismic | 1 |

The first eight titles of Q1 to Q5 were screened, and every returned title of F1 to F3, F5 to F7, and the first six of F4. Abstracts were read where OpenAlex returned one.

## What the search returned

No returned work met the rule above.

Q6, Q7, and Q8 returned zero works. F5 returned two works, both ShellBench deposits by this study's author: 10.5281/zenodo.23851675 and 10.5281/zenodo.24194143. The brief already describes ShellBench as whole-building carbon of shell floors with a rigid diaphragm. Those deposits are not a floor designed for in-plane flexibility.

Citing works, OpenAlex `cited_by_count` on the same day:

| Seed | Cited by | Citing works whose title or abstract contains the word |
|---|---|---|
| Ismail and Mueller 2021, 10.1016/j.engstruct.2021.112955 | 72 | seismic 1, diaphragm 0, earthquake 1 |
| Oval et al. 2023, 10.1016/j.istruc.2023.01.063 | 57 | seismic 0, diaphragm 0, earthquake 0 |
| Amir and Majdouba 2024, 10.1007/s00158-024-03824-9 | 7 | seismic 0, diaphragm 0, earthquake 0 |
| Whiteley et al. 2023, 10.1016/j.istruc.2023.03.116 | 21 | seismic 1, diaphragm 0, earthquake 0 |
| Chiang and Borgart, 10.1016/j.engstruct.2021.113514 | 28 | seismic 2, diaphragm 1, earthquake 2 |

The Ismail seismic and earthquake hits, and one Chiang seismic hit, had no abstract in OpenAlex. Their titles are stone-masonry floors, antiseismic devices for high-rise buildings, and seismic fragility of large-span spatial steel structures. The Whiteley seismic hit is a bibliometric study of corroded slab-column connections, 10.1007/s44290-026-00401-5. None of these is a designed concrete shell floor.

## Neighbours, from the abstracts that were returned

Fischer, Guest and Schafer 2019, DOI 10.1002/cepa.1092, optimise the layout of a floor diaphragm in a steel building for shear stiffness and weight. The lateral demand includes wind and earthquake. The 2022 journal title is "Topology optimization of steel deck building diaphragms", DOI 10.1016/j.jcsr.2022.107186. OpenAlex returned no abstract for the journal version. This is a steel deck.

Tunç, Azizi and Tanfener 2021, DOI 10.2339/politeknik.971343, compare a two-way slab with beams, a flat slab, a waffle slab, and a ribbed slab under gravity and lateral loads, and they compare construction cost.

IRJMETS 2026, DOI 10.56726/irjmets84268, compares a waffle slab with a one-way ribbed slab in a G+11 building in ETABS, to IS 1893 (Part I): 2016. The abstract says the one-way ribbed slab has better cost efficiency. It prints no percentage.

Çelebi and Kırtel 2025, DOI 10.1007/s10518-025-02191-0, assess a six-storey reinforced-concrete frame with ribbed slabs that collapsed in the 2023 Kahramanmaraş earthquakes, against a traditional slab. The abstract says the ribbed-slab periods were longer.

Olivieri, Sibille, Cocking and Nazifi Charandabi 2025, DOI 10.1016/j.mechrescom.2025.104491, form-find compressive shells under vertical and horizontal loads. The abstract names wind and earthquake, and masonry vaults.

Niiuchi, Matsumoto and Fujii 2017, DOI 10.3130/aijs.82.97, use topology optimisation for building shapes that resist vertical and seismic load. Gómez, Spencer and Carrion 2020, DOI 10.1016/j.engstruct.2020.111111, is title only in this search: topology optimisation of buildings under base excitation. OpenAlex returned no abstract.

Piluso, Fabbrocino and Pisapia 2026, DOI 10.1007/s10518-026-02623-5, give a stiffness requirement for the in-plane flexure of a diaphragm in a plan-regular building. The abstract does not design a shell floor.

Marseglia, Micelli and Aiello 2020, DOI 10.3390/heritage3030054, replace a masonry vault with an equivalent plate under horizontal forces. Giresini, Sassu, Butenweg and Alecci 2017, DOI 10.12989/eas.2017.12.4.409, use an equivalent truss macro-element for a masonry vault in a global seismic analysis.

The first six F4 titles are assessments or comparisons of waffle and ribbed slabs: 10.1680/stbu.2009.162.3.169, 10.14445/23488352/ijce-v13i8p121, 10.1080/15583058.2011.616619, 10.22214/ijraset.2021.38486, 10.22214/ijraset.2020.32692, and 10.5281/zenodo.21748786. Those papers were not read beyond the OpenAlex title and the opening of the abstract.

Michiels and Adriaenssens 2017, DOI 10.1016/j.engstruct.2017.10.043, is the paper Chiang cites on earthquake resistance of reinforced-concrete shells. OpenAlex returned the title and no abstract. The landing page did not return the abstract. The paper was not read.

Chiang and Borgart were read. The note is in `phase0/references.md`. Peripheral walls let a membrane shell carry horizontal loads without leaving its shape. The worked example is a triangular shell and a quasi-static horizontal load of 0.3 times the vertical load. It is not a floor diaphragm.

## Hypotheses

H1 to H4 stay as written in `brief.md`. This search does not rewrite them. On the bays already on file, H1 is open and H2 is not supported on the reduced model. H3 and H4 are not tested.
