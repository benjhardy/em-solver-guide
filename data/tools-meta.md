# EM tool metadata: verification notes (retrieved 2026-10-14)

`tools-meta.json` holds 56 entries. A null field means it was not verified. Price tiers are a judgement of product class, not quoted prices.

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
