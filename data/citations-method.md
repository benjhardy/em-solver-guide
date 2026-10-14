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
