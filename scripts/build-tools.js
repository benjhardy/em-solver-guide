// Build the TOOLS array from data/tools-meta.json, with short descriptions, and splice it into index.html.
// Run: node scripts/build-tools.js
const fs = require('fs');
const path = require('path');
const root = path.join(__dirname, '..');
const meta = JSON.parse(fs.readFileSync(path.join(root, 'data', 'tools-meta.json'), 'utf8'));
const NAME = {
  'HFSS-IE and HFSS SBR+': 'HFSS-IE and SBR+', 'EMX Planar 3D Solver': 'EMX', 'Sigrity (Sigrity X)': 'Sigrity', 'EMPro (PathWave EM Design)': 'EMPro',
  'Elmer FEM': 'Elmer', 'GetDP + Gmsh': 'GetDP + Gmsh (ONELAB)', 'Q3D Extractor and 2D Extractor': '2D Extractor and Q3D Extractor',
  'MMTL (TNT-MMTL)': 'MMTL', 'HyperLynx Full-Wave / HyperLynx Advanced Solvers': 'HyperLynx Advanced Solvers', 'RaptorX / Exalto': 'Exalto and RaptorX',
};
const SKIP = new Set(['VeloceRF', 'scikit-rf']);
const DESC = {
  'HFSS': 'The reference 3D FEM tool for RF and microwave design. Adaptive mesh, wave ports and an eigenmode solver.',
  'HFSS-IE and SBR+': 'Integral-equation and ray (SBR) solvers in the same desktop as HFSS.',
  'HFSS 3D Layout': 'HFSS for PCB, package and IC layouts. It also has a planar MoM solver.',
  'SIwave': 'Signal and power integrity for PCBs and packages.',
  'Exalto and RaptorX': 'On-chip EM extraction for RFIC layouts. The engines are now part of HFSS-IC.',
  'COMSOL RF Module': 'General FEM with RF physics. It can also solve coupled physics, for example heat and stress.',
  'CST Studio Suite': 'Time-domain (FIT, closely related to FDTD), frequency-domain FEM, integral-equation (MLFMM) and asymptotic solvers in one suite.',
  'AWR Analyst': '3D FEM in the AWR Microwave Office flow.',
  'AXIEM': 'Planar MoM in Microwave Office for PCB, LTCC, MMIC and RFIC passives.',
  'Clarity 3D Solver': 'Parallel 3D FEM for packages, boards and system interconnect.',
  'EMX': 'Planar integral-equation solver for RFIC passives such as spirals and transformers. Foundries certify it.',
  'Sigrity': 'Signal and power integrity analysis for PCBs and packages.',
  'EMPro': '3D FEM and FDTD that connect to ADS. Also called PathWave EM Design.',
  'Momentum': 'Planar MoM in ADS. Many MMIC and PCB teams use it as the standard layout EM check.',
  'RFPro': 'EM environment in ADS and Virtuoso. It runs Momentum and 3D FEM directly on the layout.',
  'JCMsuite': 'Higher-order FEM for nano-optics and photonics.',
  'Palace': 'Parallel 3D FEM for frequency-domain, eigenmode, transient, electrostatic and magnetostatic problems. Built on MFEM. It has no GUI.',
  'Elmer': 'Multiphysics FEM with a vector Helmholtz module for time-harmonic EM.',
  'NGSolve': 'High-order FEM library with Python scripts. It includes Maxwell examples.',
  'GetDP + Gmsh (ONELAB)': 'Flexible FEM solver with the Gmsh mesher.',
  'XFdtd': 'FDTD with conformal mesh, GPU speed-up and strong SAR and antenna tools.',
  'QuickWave': 'Conformal FDTD for microwave devices, antennas and microwave heating.',
  'Sim4Life': 'FDTD for bio-EM and MRI safety, with anatomical body models.',
  'EMPIRE XPU': 'Fast FDTD for antennas and planar circuits.',
  'Lumerical FDTD': 'The common FDTD tool for photonics and nanophotonics.',
  'RSoft FullWAVE': 'FDTD for photonic devices. Keysight bought it from Synopsys in October 2025.',
  'Tidy3D': 'GPU FDTD on the vendor cloud. The Python client is open source.',
  'Simcenter Feko': 'MoM and MLFMM are the core. It also has FEM, FDTD, PO, ray methods and hybrids between them.',
  'openEMS': 'EC-FDTD with Python and MATLAB or Octave scripts. Frequently used for antennas and PCB structures.',
  'MEEP': 'FDTD for photonics and nanophotonics with a Python interface.',
  'gprMax': 'FDTD for ground-penetrating radar, with GPU support.',
  'WIPL-D Pro': '3D MoM with higher-order basis functions. Efficient for large metal and dielectric bodies.',
  'ESTEAM': 'Higher-order MoM and MLFMM for antennas and reflector feeds.',
  'NEC-2': 'The classic wire MoM code. Most amateur and HF antenna tools use it.',
  '4nec2': 'Free Windows interface for NEC, with optimisation and plots.',
  'Bempp-cl': 'Boundary element (MoM) library in Python for Maxwell and acoustic problems.',
  'Sonnet Suites': '2.5D MoM in a closed box, with an FFT-calculated box Green\'s function on a uniform cell grid.',
  'Sonnet Lite': 'Free version of Sonnet. Limits: 6 ports, 64 MB, 2 metal levels. You can use it to learn planar EM.',
  'GRASP': 'The standard tool for reflector antennas. It uses PO, PTD and UTD.',
  'XGtd': 'GO and UTD ray tracing for antenna placement and coupling on large platforms such as aircraft and ships.',
  'Wireless InSite': 'Ray tracing for radio propagation in cities, buildings and vehicles.',
  'Sionna RT': 'Differentiable ray tracer for radio propagation, with Python scripts.',
  'POFacets': 'MATLAB physical-optics RCS code for faceted models. Frequently used to teach RCS.',
  '2D Extractor and Q3D Extractor': 'Cross-section RLGC and quasi-static 3D parasitic extraction.',
  'Si9000e': 'Boundary-element field solver for PCB transmission-line impedance.',
  'FastHenry and FastCap': 'Quasi-static inductance and capacitance extraction.',
  'ASITIC': 'Classic tool to analyse and design on-chip spiral inductors. No longer developed.',
  'MMTL': 'Multilayer transmission-line cross-section solver with the boundary-element method. No longer developed.',
  'HyperLynx Advanced Solvers': 'Full-wave and quasi-static solvers for PCB signal integrity.',
  'Simbeor': 'Signal-integrity tool for PCB and package interconnects.',
  'µWave Wizard': 'Mode-matching solver with FEM and MoM parts, for waveguide filters, feeds and couplers.',
  'gds2palace': 'Converts IHP SG13G2 GDSII layouts into Palace models. It is not a solver.',
  'gds2openEMS': 'Converts IHP SG13G2 GDSII layouts into openEMS models. It is not a solver.',
  'OpenParEM': 'Open-source parallel FEM for 2D port modes and 3D S-parameters.',
  'scuff-em': 'Surface-integral (BEM) solver for scattering. No longer developed.',
};
const LIC = { commercial: 'c', open: 'o', free: 'f' };
const out = [];
for (const t of meta.tools) {
  if (SKIP.has(t.name)) continue;
  const base = {
    owner: t.owner.replace(/\s*\(.*$/, '').replace(/\.$/, ''), m: t.methods || [], dom: t.domains || [], price: t.price_tier, trial: t.trial,
    api: t.api || null, gpu: t.gpu, hpc: t.hpc, os: t.os || null, imp: t.import || null, eda: t.eda_link || null, cloud: !!t.cloud_only, mat: t.maturity, url: t.url,
  };
  if (t.name === 'Sonnet Suites and Sonnet Lite') {
    out.push({ n: 'Sonnet Suites', lic: 'c', ...base, trial: 'trial', d: DESC['Sonnet Suites'] });
    out.push({ n: 'Sonnet Lite', lic: 'f', ...base, price: 'free', trial: null, d: DESC['Sonnet Lite'] });
    continue;
  }
  const n = NAME[t.name] || t.name;
  if (!DESC[n]) { console.log('NO DESC', n); continue; }
  out.push({ n, lic: LIC[t.licence] || 'c', ...base, d: DESC[n], helper: /not a solver/.test(DESC[n]) || undefined });
}
// corrections from review round 2 (field tags, methods, unverified EDA links), plus field standards and validation notes
const FIX = {
  'openEMS': { dom: ['rf', 'antenna', 'rfic', 'bioem', 'pcb_si'] },
  'Palace': { dom: ['rf', 'rfic', 'antenna'] },
  'Exalto and RaptorX': { m: ['mom25', 'mom3d'] },
  'CST Studio Suite': { eda: null },
  'Simcenter Feko': { eda: null },
  'µWave Wizard': { d: 'Mode-matching solver (with FEM and MoM parts) for waveguide filters, feeds and couplers. The page lists it under FEM.' },
};
const STD = {
  'EMX': ['rfic'], 'Momentum': ['rfic', 'rf'], 'RFPro': ['rfic'], 'Exalto and RaptorX': ['rfic'], 'AXIEM': ['rf'],
  'XFdtd': ['bio', 'antenna'], 'Sim4Life': ['bio'], 'HFSS': ['antenna', 'rf', 'pcb'], 'CST Studio Suite': ['antenna', 'rf', 'emc'], 'Simcenter Feko': ['antenna', 'emc'],
  'SIwave': ['pcb'], 'Sigrity': ['pcb'], 'HyperLynx Advanced Solvers': ['pcb'], 'Lumerical FDTD': ['photonics'], 'Tidy3D': ['photonics'],
  'Wireless InSite': ['prop'], 'gprMax': ['prop'], 'GRASP': ['antenna'], 'openEMS': ['free'], 'Sonnet Lite': ['free'],
};
const VALID = { 'XFdtd': 'States IEC/IEEE 62704-1 SAR averaging', 'Sim4Life': 'States IEC/IEEE 62704-1 SAR averaging', 'HFSS': 'Has an IEC/IEEE 62704-4 draft SAR setting', 'EMX': 'Foundry-certified for many processes' };
// tools added after review (Ben, 2026-10-14); sources: remcom.com/wavefarer-automotive-radar-software, remcom.com/radar-and-scattering
out.splice(out.findIndex((t) => t.n === 'Wireless InSite'), 0, { n: 'WaveFarer', lic: 'c', owner: 'Remcom', m: ['asym'], dom: ['radar', 'antenna'], price: null, trial: null, api: null, gpu: null, hpc: null, os: null, imp: null, eda: null, cloud: false, mat: 'production', url: 'https://www.remcom.com/wavefarer-automotive-radar-software',
  d: 'Radar simulation with ray tracing: PO and equivalent currents for scattering, GO and UTD for multipath. For automotive and indoor radar scenes and far-field RCS, up to more than 100 GHz.' });
// radar and RCS field
['XGtd', 'Simcenter Feko', 'HFSS-IE and SBR+', 'CST Studio Suite', 'POFacets', 'WIPL-D Pro'].forEach((n) => { const t = out.find((x) => x.n === n); if (t && !t.dom.includes('radar')) t.dom.push('radar'); });
STD['WaveFarer'] = ['radar']; STD['XGtd'] = ['radar', 'antenna']; STD['HFSS-IE and SBR+'] = ['radar']; STD['Simcenter Feko'] = ['antenna', 'emc', 'radar'];
out.forEach((t) => { if (FIX[t.n]) Object.assign(t, FIX[t.n]); if (STD[t.n]) t.std = STD[t.n]; if (VALID[t.n]) t.valid = VALID[t.n]; if (t.owner === 'Dassault Systemes') t.owner = 'Dassault Systèmes'; });
// owner text tidy-ups
out.forEach((t) => { if (t.owner.startsWith('Ansys, part of Synopsys')) t.owner = 'Ansys (part of Synopsys)'; });
const p = path.join(root, 'index.html');
let s = fs.readFileSync(p, 'utf8');
const a = s.indexOf('  const TOOLS = ['), b = s.indexOf('  const LIC = {');
s = s.slice(0, a) + '  // tool data: vendor pages and docs, checked ' + meta.retrieved + ' (tools-meta.json)\n  const TOOLS = ' + JSON.stringify(out) + ';\n' + s.slice(b);
fs.writeFileSync(p, s);
console.log('tools', out.length);
