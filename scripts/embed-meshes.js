// Embed meshes/<id>.json into index.html as gzip + base64 strings, so the page works as one file.
// Run after scripts/meshgen.py:  node scripts/embed-meshes.js
const fs = require('fs');
const path = require('path');
const zlib = require('zlib');
const root = path.join(__dirname, '..');
const dir = path.join(root, 'meshes');
const out = {};
for (const f of fs.readdirSync(dir).filter((f) => f.endsWith('.json')).sort()) {
  out[f.replace(/\.json$/, '')] = zlib.gzipSync(fs.readFileSync(path.join(dir, f)), { level: 9 }).toString('base64');
}
const p = path.join(root, 'index.html');
let s = fs.readFileSync(p, 'utf8');
const re = /<script type="application\/json" id="meshdata">[\s\S]*?<\/script>/;
if (!re.test(s)) throw new Error('meshdata slot not found');
s = s.replace(re, `<script type="application/json" id="meshdata">${JSON.stringify(out)}</script>`);
fs.writeFileSync(p, s);
console.log('embedded', Object.keys(out).length, 'meshes,', Math.round(JSON.stringify(out).length / 1024), 'kB');
