const fs = require('fs');
const html = fs.readFileSync('Painel_FPD_Regional_Norte.html', 'utf8');
const pStart = html.indexOf('const PAYLOAD = ') + 'const PAYLOAD = '.length;
const pEnd = html.indexOf('/* ============ decodificação');
const payload = JSON.parse(html.substring(pStart, pEnd).trim().replace(/;$/, ''));
for (const [k, v] of Object.entries(payload.dicts)) {
  console.log(`${k} (${v.length}):`, v.slice(0, 5));
}
