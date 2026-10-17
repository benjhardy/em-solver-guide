# EM tool metadata: verification notes (retrieved 2026-10-14)

`tools-meta.json` holds 62 entries (56 checked 2026-10-14, 6 added 2026-10-17, see the last section). A null field means it was not verified. Price tiers are a judgement of product class, not quoted prices.

## Verified
- **Ownership:** checked against press releases, SEC filings or vendor pages (list below).
- **Open-source licences:** read from the GitHub API or the project sites. Palace Apache-2.0, openEMS GPL-3.0, MEEP GPL-2.0, gprMax GPL-3.0, NGSolve LGPL-2.1, Elmer GPL-2.0, GetDP GPL-2.0+, Bempp-cl MIT, scuff-em GPL-2.0, OpenParEM GPL-3.0+, Sionna RT Apache-2.0, gds2palace and gds2openEMS GPL-3.0, scikit-rf BSD-3, Tidy3D client LGPL-2.1.
- **Free and student editions:** HFSS (Electronics Desktop Student: 64k volume elements, 4 cores), CST Learning Edition, Sonnet Lite (6 ports, 64 MB, 2 metal levels), TICRA Tools Student Edition, Sim4Life Lite, Altair Feko student edition.
- **Trials:** COMSOL, JCMsuite (14 days), WIPL-D (30-day demo), Remcom, Keysight ADS evaluation, Cadence AWR (8 h or 30 days, card required), Simbeor, µWave Wizard.
- **GPU support:** Palace, Lumerical (multi-node from 2025 R2), RSoft FullWAVE (2024.09), EMPro FDTD, ADS FEM (cuDSS), QuickWave (OpenCL), WIPL-D, Wireless InSite, Sim4Life. EMPIRE uses CPU-only "XPU" acceleration.
- **SAR:** XFdtd (vendor-verified to 62704-1), Sim4Life (62704-1 averaging) and HFSS (a "62704-4 Draft" setting). openEMS says its SAR averaging is not validated.

## Uncertain
- Some fields come from my own knowledge and were not checked on vendor pages, because cadence.com and keysight.com block automated fetches: API names, import formats and EDA links for Cadence and Keysight tools, CST, Feko, AWR and EMX.
- The 62704 status of CST, COMSOL, Feko, EMPIRE and QuickWave: no public statement found either way.
- The CST Learning Edition mesh cap: about 80k tetrahedra and 1 core, from a table that was hard to parse.
- Whether HFSS Student excludes SBR+: seen only in search snippets.
- Sonnet Lite's 3-dielectric-layer limit: the source page is now a 404.
- Feko student edition: unclear whether it continues under Siemens.
- VeloceRF's EM engine, and whether Virtuoso is still supported (the current page names only Custom Compiler).
- Methods for RaptorX, Simbeor and SIwave are simplified to the nearest category.

## Ownership changes since 2024
- **Ansys → Synopsys:** closed 17 Jul 2025. Ansys URLs now redirect to ansys.synopsys.com. VeloceRF and Exalto are now on synopsys.com as "Synopsys VeloceRF" and "Synopsys Exalto". RaptorX has no standalone page; it ships inside HFSS-IC and RaptorH.
- **Synopsys Optical Solutions Group, including RSoft → Keysight:** closed 17 Oct 2025, together with Ansys PowerArtist. Lumerical stayed with Ansys/Synopsys.
- **Altair → Siemens:** closed 26 Mar 2025. Altair Feko is now Simcenter Feko.

## Renamed or changed
- CST "Student Edition" is now the **Learning Edition**.
- Sonnet **Lite Plus** was discontinued; its features are now in Lite.
- The `openems_ihp_sg13g2` repo was renamed **gds2openEMS**. Both IHP helpers are hosted on Volker Muehlhaus's personal GitHub, not the IHP-GmbH organisation, and are on PyPI.
- EMPro 2026 dropped its built-in cluster submission.
- **Likely unmaintained:** ASITIC, scuff-em (no commits since 2020), MMTL.

## Added 2026-10-17
Six tools, checked on vendor pages and documentation on 17 Oct 2026. Sources are in each record.
- **Nullspace EM** (Nullspace, Inc.): spun out of IERUS Technologies, independent since 2023 (about page; IERUS product page). Verified on vendor pages: frequency-domain surface-integral-equation MoM, high-order geometry and basis functions, conductors, dielectrics and magnetic materials, adaptive matrix compression and a fast direct solver, multi-CPU/multi-GPU (NVIDIA Kepler or later), Windows 10/11 and RHEL, Python API, 1-month trial for qualified customers, academic licences at a nominal (waivable) cost with no feature limits, per-node lease or paid-up licences. Not stated anywhere: the compression algorithm (no MLFMM, H-matrix or ACA named), MPI/cluster runs, CAD import formats (Nullspace Prep, built with Coreform, says only "standard and proprietary CAD formats"), the EFIE/CFIE/PMCHWT choice, prices. The licence pages disagree (per node vs floating). Benchmark speed-ups are vendor claims. Nullspace ES (electrostatic MoM for ion traps) is described in the note, not as a separate record, because the guide has no quantum/electrostatics field.
- **NEC-4** (LLNL): NEC-4.2, licensed by LLNL (3-year licences from $110; free for US government and contractors). OS, GPU and source terms not stated. NEC-5 is mentioned only on eznec.com.
- **EZNEC** (Roy Lewallen, W7EL): Pro/2+ v7.0 free with no support, Windows 7+, 45,000 segments, NEC-2 engine plus external NEC-4.2/NEC-5. "Free since January 2022" is from a news report (kb6nu.com). Public-domain status is claimed only in secondary sources and is not used.
- **MMANA-GAL**: MININEC-3 engine; basic 3.5 free for private non-commercial use only; PRO 3.3 paid. OS not stated on the developer page. gal-ana.de fails HTTPS certificate checks; the HTTP page was read.
- **WinProp**: owner Siemens via Altair (Altair bought AWE Communications in April 2016). The 2025/2026 docs still say "Altair WinProp"; a Siemens blog post (12 Jun 2026) uses "Simcenter Feko WinProp 2026.1". Windows and Linux, API and WinPropCLI, DXF/DWG building import verified in the docs. GPU, trial and student status not confirmed.
- **Perceive EM** (Ansys, part of Synopsys): exists as a distinct product page. PO-based SBR with multipath and diffraction on NVIDIA GPUs, headless Python/C++ API. The "new in 2024 R2" date is from a CADFEM summary seen only in a search snippet (the page returned 403); the Ansys 2024 R2 press release does not name it. OS, licence and trial not stated.
