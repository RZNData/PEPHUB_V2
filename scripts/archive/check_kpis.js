const fs = require('fs');
const html = fs.readFileSync('Painel_FPD_Regional_Norte.html', 'utf8');

const dIdx = html.indexOf('const MATUR');
if (dIdx !== -1) {
  console.log('=== MATUR BLOCK ===');
  console.log(html.substring(Math.max(0, dIdx - 100), dIdx + 800));
} else {
  console.log('MATUR not found');
}
