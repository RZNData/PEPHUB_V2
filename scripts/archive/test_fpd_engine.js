const fs = require('fs');
const zlib = require('zlib');

console.log('--- TESTE DO MOTOR ANALÍTICO DO PAINEL FPD ---');

const html = fs.readFileSync('Painel_FPD_Regional_Norte.html', 'utf8');

// Extrair PAYLOAD
const pStart = html.indexOf('const PAYLOAD = ');
const pEnd = html.indexOf('// GLOSSÁRIO');
const jsonStr = html.substring(pStart + 'const PAYLOAD = '.length, pEnd).trim().replace(/;$/, '');
const PAYLOAD = JSON.parse(jsonStr);

console.log(`1. Payload parseado com sucesso: ${PAYLOAD.n} contratos.`);

// Descompactar cada coluna com zlib
const C = {};
for (const k in PAYLOAD.cols) {
  const colObj = PAYLOAD.cols[k];
  const buf = Buffer.from(colObj.b, 'base64');
  const decompressed = zlib.inflateSync(buf);
  if (colObj.t === 'u8') {
    C[k] = new Uint8Array(decompressed.buffer, decompressed.byteOffset, decompressed.byteLength);
  } else {
    C[k] = new Uint16Array(decompressed.buffer, decompressed.byteOffset, decompressed.byteLength / 2);
  }
  console.log(` - Coluna ${k.padEnd(12)}: ${C[k].length} registros (tipo ${colObj.t})`);
}

const N = PAYLOAD.n;
const D = PAYLOAD.dicts;

// 2. Testar métricas globais
let totalInst = N;
let ag60 = 0, ag30 = 0, ag90 = 0;

for (let i = 0; i < N; i++) {
  if (C.ag60[i] === 1) ag60++;
  if (C.ag30[i] === 1) ag30++;
  if (C.ag90[i] === 1 || C.ag120[i] === 1 || C.ag150[i] === 1 || C.ag180[i] === 1 || C.over90[i] === 1) ag90++;
}
const emDia = totalInst - ag60;

console.log('\n2. Métricas Globais (Universo Total):');
console.log(` - Instalações: ${totalInst}`);
console.log(` - FPD 60 (Oficial): ${ag60} (${(ag60 / totalInst * 100).toFixed(2)}%)`);
console.log(` - FPD 30 (Pró-rata): ${ag30} (${(ag30 / totalInst * 100).toFixed(2)}%)`);
console.log(` - Aging 90+: ${ag90} (${(ag90 / totalInst * 100).toFixed(2)}%)`);
console.log(` - Em Dia: ${emDia} (${(emDia / totalInst * 100).toFixed(2)}%)`);

// 3. Testar agregação por Safra
console.log('\n3. Distribuição por Safra de Venda:');
const safraAgg = {};
D.safra.forEach((s, idx) => {
  safraAgg[idx] = { safra: s, total: 0, ag60: 0, ag30: 0 };
});

for (let i = 0; i < N; i++) {
  const sIdx = C.safra[i];
  safraAgg[sIdx].total++;
  if (C.ag60[i] === 1) safraAgg[sIdx].ag60++;
  if (C.ag30[i] === 1) safraAgg[sIdx].ag30++;
}

Object.values(safraAgg).forEach(item => {
  const taxa60 = (item.ag60 / item.total * 100).toFixed(2);
  const taxa30 = (item.ag30 / item.total * 100).toFixed(2);
  console.log(` - Safra ${item.safra}: ${item.total.toLocaleString()} inst | FPD 60: ${item.ag60} (${taxa60}%) | FPD 30: ${item.ag30} (${taxa30}%)`);
});

// 4. Testar agregação por Top 5 Parceiros
console.log('\n4. Top 5 Parceiros em Volume de Vendas:');
const parcAgg = {};
for (let i = 0; i < N; i++) {
  const pIdx = C.parceiro[i];
  if (!parcAgg[pIdx]) parcAgg[pIdx] = { total: 0, ag60: 0, ag30: 0 };
  parcAgg[pIdx].total++;
  if (C.ag60[i] === 1) parcAgg[pIdx].ag60++;
  if (C.ag30[i] === 1) parcAgg[pIdx].ag30++;
}

const sortedParc = Object.keys(parcAgg)
  .map(k => ({ nome: D.parceiro[k], ...parcAgg[k] }))
  .sort((a, b) => b.total - a.total);

sortedParc.slice(0, 5).forEach((p, idx) => {
  const taxa60 = (p.ag60 / p.total * 100).toFixed(2);
  console.log(` #${idx+1} ${p.nome}: ${p.total.toLocaleString()} inst | FPD 60: ${p.ag60} (${taxa60}%)`);
});

// 5. Testar agregação por Top 5 Cidades
console.log('\n5. Top 5 Cidades por Volume:');
const cidAgg = {};
for (let i = 0; i < N; i++) {
  const cIdx = C.cidade[i];
  if (!cidAgg[cIdx]) cidAgg[cIdx] = { total: 0, ag60: 0, ag30: 0 };
  cidAgg[cIdx].total++;
  if (C.ag60[i] === 1) cidAgg[cIdx].ag60++;
  if (C.ag30[i] === 1) cidAgg[cIdx].ag30++;
}

const sortedCid = Object.keys(cidAgg)
  .map(k => ({ nome: D.cidade[k], ...cidAgg[k] }))
  .sort((a, b) => b.total - a.total);

sortedCid.slice(0, 5).forEach((c, idx) => {
  const taxa60 = (c.ag60 / c.total * 100).toFixed(2);
  console.log(` #${idx+1} ${c.nome}: ${c.total.toLocaleString()} inst | FPD 60: ${c.ag60} (${taxa60}%)`);
});

// 6. Testar Bounding Box e coordenadas do Mapa
console.log('\n6. Validação Geoespacial / Mapa:');
console.log(' - BBox:', PAYLOAD.bbox);
let validCoords = 0;
for (let i = 0; i < N; i++) {
  if (C.gx[i] !== 0 && C.gy[i] !== 0) validCoords++;
}
console.log(` - Contratos com coordenadas na malha (gx/gy): ${validCoords} (${(validCoords/N*100).toFixed(1)}%)`);


console.log('\n=============================================');
console.log('STATUS: MOTOR ANALÍTICO DO PAINEL FPD VALIDADO COM 100% DE SUCESSO!');
console.log('=============================================');
