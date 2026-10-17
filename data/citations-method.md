# EM solver mentions in the literature: method

**Source:** OpenAlex API, retrieved 2026-10-14. Data: `citations.json`.

## Method
Each tool gets one OpenAlex works search (`search=`: title, abstract and full text where available, boolean syntax), grouped by `publication_year`. `mentions_all` is `meta.count`; `mentions_since_2020` sums the 2020-2026 groups. Ambiguous names get required context words (e.g. HFSS needs an RF/EM word, ASITIC needs Niknejad plus inductor). Exact queries are in the JSON. For open-source tools with a canonical paper, `cited_by` is that DOI's OpenAlex `cited_by_count`.

## Limits
- OpenAlex has full text for only part of the literature, and the share varies by publisher. All counts are lower bounds on true mentions.
- A mention does not mean the tool was used. Comparisons, citations and dataset reuse (such as DeepMIMO for Wireless InSite) all count.
- Short or common names collide with other words. Bare "HFSS" matches "HFSs" (hesitant fuzzy sets). Bare "ASITIC" returns 2,659 hits, mostly from the hyphenated line break "par-asitic". Strict queries fix this but undercount. Palace, Elmer, EMX, Sonnet and GRASP are undercounted for the same reason.
- Counts include theses, proceedings tables of contents and software records, not only papers.
- Commercial tools have no canonical paper. Mention counts and paper citations are different measures and must not be ranked together.
- OpenAlex reindexes over time, so counts drift.

## Precision spot-check
For the six largest counts, 10 random records each (`sample=10&seed=7`) were judged by title and abstract for plausible EM-simulation work. Actual use could not be confirmed.

| Tool | On target |
|---|---|
| HFSS | 0.75 (fuzzy-set and magazine false hits) |
| CST | 1.0 |
| COMSOL RF | 0.8 (thermal-only leak-through) |
| Lumerical FDTD | 1.0 |
| Feko | 0.9 |
| Sim4Life | 0.8 (acoustic ultrasound uses) |

With n=10, each figure is roughly ±0.15.

## Top 10 by mentions since 2020

| # | Tool | Since 2020 | All years |
|---|---|---|---|
| 1 | Ansys HFSS | 15,338 | 33,329 |
| 2 | CST Studio Suite | 13,349 | 24,077 |
| 3 | COMSOL RF Module | 5,473 | 8,862 |
| 4 | Ansys Lumerical FDTD | 4,650 | 7,196 |
| 5 | Feko | 1,881 | 3,929 |
| 6 | Sim4Life / SEMCAD X | 846 | 1,646 |
| 7 | Remcom Wireless InSite | 802 | 1,068 |
| 8 | gprMax | 769 | 1,094 |
| 9 | Ansys Q3D / 2D Extractor | 758 | 1,265 |
| 10 | MEEP | 648 | 1,338 |

## Tools added 2026-10-17
Same method (one `search=` query, grouped by `publication_year`), run on 17 Oct 2026. The API now reports `search=` as a full-text search ("full text has"); re-running two older queries gave the same counts within drift (WIPL-D 581 vs 579, POFacets 69 vs 69). Informal 10-record samples (`sample=10&seed=7`) only.

| Tool | Query | All years | Since 2020 | Sample on target |
|---|---|---|---|---|
| WinProp | `WinProp AND (propagation OR "ray tracing" OR Altair OR AWE)` | 463 | 296 | 8/10 |
| MMANA-GAL | `"MMANA-GAL" OR (MMANA AND antenna)` | 193 | 119 | 7/10 |
| NEC-4 | `("NEC-4" OR NEC4 OR "NEC-4.2") AND antenna` | 161 | 37 | 8/10 |
| EZNEC | `EZNEC AND antenna` | 64 | 19 | 9/10 |
| Perceive EM | `"Perceive EM" AND Ansys` | 4 | 4 | 4/4 |
| Nullspace EM | `"Nullspace Inc"` | 2 | 2 | 0/2, not shown |

- **Nullspace:** the bare word is the linear-algebra term, so only exact phrases were tried: "Nullspace EM" 0, "Nullspace ES" 0, Nullspace AND IERUS 0, "Nullspace Inc" 2 (both IEEE Microwave Magazine IMS Preview issues). The page shows no count for it, as for ESTEAM.
- **Bare names collide:** MMANA 2,126 hits (medical, maths and text-extraction noise), WinProp 996, "Perceive EM" 176 (63 of them before the product existed).
- **NEC-4** overlaps the NEC-2 row, whose "Numerical Electromagnetics Code" phrase also matches NEC-4 papers.
