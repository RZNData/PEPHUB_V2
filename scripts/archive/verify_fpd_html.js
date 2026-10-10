const fs = require('fs');
const zlib = require('zlib');

console.log('Testando Painel_FPD_Regional_Norte.html...');
const html = fs.readFileSync('Painel_FPD_Regional_Norte.html', 'utf8');

const marker = 'const PAYLOAD = ';
const startIdx = html.indexOf(marker);
if (startIdx === -1) {
  console.error('ERRO: Marker const PAYLOAD não encontrado!');
  process.exit(1);
}

const afterMarker = html.substring(startIdx + marker.length);
const endIdx = afterMarker.indexOf(';\n\n// GLOSSÁRIO');
if (endIdx === -1) {
  console.error('ERRO: Fim do PAYLOAD não encontrado!');
  process.exit(1);
}

const jsonStr = afterMarker.substring(0, endIdx);
console.log('Tamanho da string JSON:', jsonStr.length, 'bytes');
const payload = JSON.parse(jsonStr);

console.log('JSON Parse OK!');
console.log('Contratos:', payload.n);
console.log('Cidades:', payload.dicts.cidade.length);
console.log('Parceiros:', payload.dicts.parceiro.length);
console.log('Vendedores:', payload.dicts.vendedor.length);
console.log('Canais:', payload.dicts.canal.length);
console.log('Faixas de Risco:', payload.dicts.risco.length);
console.log('Bounding Box:', payload.bbox);

// Calcular totais
let c60 = 0, c30 = 0;
const n = payload.n;
for (let i = 0; i < n; i++) {
  if (payload.cols.aging60[i] === 1) c60++;
  if (payload.cols.aging30[i] === 1) c30++;
}
console.log(`FPD 60: ${c60} (${(c60/n*100).toFixed(2)}%)`);
console.log(`FPD 30: ${c30} (${(c30/n*100).toFixed(2)}%)`);
console.log('VALIDAÇÃO CONCLUÍDA COM SUCESSO TOTAL!');

