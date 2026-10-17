// Build the compact CITES constant from data/citations.json and splice it into index.html.
// Run: node scripts/embed-citations.js
const fs = require('fs');
const path = require('path');
const root = path.join(__dirname, '..');
const c = JSON.parse(fs.readFileSync(path.join(root, 'data', 'citations.json'), 'utf8'));
const DISPLAY = {
  'Ansys HFSS': 'HFSS', 'Ansys HFSS-IE / HFSS SBR+': 'HFSS-IE and SBR+', 'COMSOL Multiphysics RF Module': 'COMSOL RF Module',
  'CST Studio Suite (CST Microwave Studio)': 'CST Studio Suite', 'Cadence AWR AXIEM / AWR Analyst': 'AXIEM / AWR Analyst',
  'Cadence Clarity 3D Solver': 'Clarity 3D Solver', 'Cadence EMX': 'EMX', 'Keysight EMPro': 'EMPro', 'Keysight ADS Momentum': 'Momentum',
  'Keysight RFPro': 'RFPro', 'JCMsuite': 'JCMsuite', 'Palace': 'Palace', 'Elmer FEM': 'Elmer', 'NGSolve': 'NGSolve', 'GetDP': 'GetDP', 'MFEM': 'MFEM',
  'Remcom XFdtd': 'XFdtd', 'ZMT Sim4Life / SEMCAD X': 'Sim4Life', 'IMST EMPIRE XPU': 'EMPIRE XPU', 'Ansys Lumerical FDTD': 'Lumerical FDTD',
  'Synopsys RSoft FullWAVE': 'RSoft FullWAVE', 'Flexcompute Tidy3D': 'Tidy3D', 'QWED QuickWave': 'QuickWave', 'Altair Feko': 'Simcenter Feko',
  'openEMS': 'openEMS', 'MEEP': 'MEEP', 'gprMax': 'gprMax', 'WIPL-D': 'WIPL-D Pro', 'TICRA GRASP': 'GRASP', 'NEC-2 / NEC (and 4nec2)': 'NEC-2',
  'Bempp-cl': 'Bempp-cl', 'Sonnet (incl. Sonnet Lite)': 'Sonnet Suites', 'Remcom Wireless InSite': 'Wireless InSite', 'Remcom XGtd': 'XGtd',
  'Sionna RT': 'Sionna RT', 'POFacets': 'POFacets', 'Ansys Q3D Extractor / 2D Extractor': '2D Extractor and Q3D Extractor',
  'Polar Instruments Si9000': 'Si9000e', 'FastHenry': 'FastHenry', 'FastCap': 'FastCap', 'ASITIC': 'ASITIC', 'MMTL': 'MMTL',
  'Nullspace EM': 'Nullspace EM', 'NEC-4': 'NEC-4', 'EZNEC': 'EZNEC', 'MMANA-GAL': 'MMANA-GAL', 'WinProp': 'WinProp', 'Ansys Perceive EM': 'Perceive EM',
};
// mention counts that the research agent marked as not reliable
const NO_MENTIONS = new Set(['TICRA ESTEAM', 'ASITIC', 'Cadence AWR Microwave Office', 'Nullspace EM']);
const tools = [];
for (const t of c.tools) {
  const n = DISPLAY[t.name];
  if (!n) { console.log('skip', t.name); continue; }
  const row = { n, k: t.methods[0], lic: t.license };
  if (!NO_MENTIONS.has(t.name) && typeof t.mentions_since_2020 === 'number') row.s20 = t.mentions_since_2020;
  if (t.canonical_paper && typeof t.canonical_paper.cited_by === 'number') row.cited = t.canonical_paper.cited_by;
  if (row.s20 == null && row.cited == null) continue;
  tools.push(row);
}
// CST: list it with its time-domain solver colour
const [Y, Mo, Dd] = c.retrieved.split('-').map(Number); const MONTHS = ['January','February','March','April','May','June','July','August','September','October','November','December'];
const method = 'Method: on ' + Dd + ' ' + MONTHS[Mo - 1] + ' ' + Y +
  ' (17 October 2026 for NEC-4, EZNEC, MMANA-GAL, WinProp and Perceive EM), we searched the OpenAlex database for each tool name in titles, abstracts and full texts. Names with other meanings (for example HFSS and Palace) have context words. ' +
  'The counts are minimum values, because OpenAlex does not have the full text of all papers. A mention does not prove that the authors used the tool. ' +
  'For the six largest counts, a sample of 10 papers each showed 75 to 100 percent relevant results. Strict queries make Palace, Elmer, EMX, Sonnet and GRASP too low. ' +
  'The main-paper chart uses the OpenAlex citation count of one paper for each open-source tool.';
const CITES = { retrieved: c.retrieved, method, tools };
const p = path.join(root, 'index.html');
let s = fs.readFileSync(p, 'utf8');
const a = s.indexOf('/*CITES-START*/'), b = s.indexOf('/*CITES-END*/');
s = s.slice(0, a) + '/*CITES-START*/\n  const CITES = ' + JSON.stringify(CITES) + ';\n  ' + s.slice(b);
fs.writeFileSync(p, s);
console.log('embedded', tools.length, 'rows');
