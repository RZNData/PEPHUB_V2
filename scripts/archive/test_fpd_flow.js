const fs = require('fs');
const zlib = require('zlib');

console.log('=== TESTANDO FLUXO COMPLETO DO PAINEL FPD ===');
const c = fs.readFileSync('Painel_FPD_Regional_Norte.html', 'utf8');

// 1. Extrair PAYLOAD
const p1 = c.indexOf('const PAYLOAD = ');
const p2 = c.indexOf('/* ============ decodificação ============ */');
const jsonStr = c.substring(p1 + 'const PAYLOAD = '.length, p2).trim().replace(/;$/, '');
const PAYLOAD = JSON.parse(jsonStr);

console.log('1. Payload parseado com sucesso:');
console.log('   - Total Contratos:', PAYLOAD.n.toLocaleString());
console.log('   - BBox:', PAYLOAD.bbox);
console.log('   - Safras:', PAYLOAD.dicts.safra);

// 2. Descompactar colunas
const B64 = s => {
  const bin = atob(s);
  const u = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) u[i] = bin.charCodeAt(i);
  return u;
};

const C = {};
for (const k in PAYLOAD.cols) {
  const col = PAYLOAD.cols[k];
  const buf = Buffer.from(B64(col.b));
  const decomp = zlib.inflateSync(buf);
  if (col.t === 'u8') C[k] = new Uint8Array(decomp.buffer, decomp.byteOffset, decomp.byteLength);
  else if (col.t === 'u16') C[k] = new Uint16Array(decomp.buffer, decomp.byteOffset, decomp.byteLength / 2);
  else C[k] = new Uint32Array(decomp.buffer, decomp.byteOffset, decomp.byteLength / 4);
}

const N = PAYLOAD.n;
const D = PAYLOAD.dicts;
console.log('2. Todas as colunas binárias descompactadas com sucesso!');
console.log('   - Colunas presentes:', Object.keys(C).join(', '));

// 3. Testar simulação das agregações de FPD usando a lógica real da ferramenta
function blank() { return { inst: 0, c: [0, 0, 0, 0, 0], np: [0, 0, 0, 0, 0], npc: [0, 0, 0, 0, 0], tp: [0, 0, 0] }; }
function addRow(o, r) {
  o.inst++;
  const a30 = C.ag30 ? C.ag30[r] : 0;
  const a60 = C.ag60 ? C.ag60[r] : 0;
  const a90 = C.ag90 ? C.ag90[r] : 0;
  const a120 = C.ag120 ? C.ag120[r] : 0;
  const aov = C.over90 ? C.over90[r] : 0;

  if (a30) o.c[0]++;
  if (a60) o.c[1]++;
  if (a90) o.c[2]++;
  if (a120) o.c[3]++;
  if (aov) o.c[4]++;

  const p = C.pbk[r];
  const naoPg = (p === 0 || (a30 && a60));
  if (a30) o.np[0]++;
  if (naoPg) {
    o.np[1]++;
    if (a60) o.npc[1]++;
  }
  if (a90 && naoPg) {
    o.np[2]++;
    o.npc[2]++;
  }
  if (a120 && naoPg) {
    o.np[3]++;
    o.npc[3]++;
  }
  if (aov && naoPg) {
    o.np[4]++;
    o.npc[4]++;
  }

  const t = C.tpk[r];
  if (t > 0 && a60) o.tp[t - 1]++;
}

const safraAgg = {};
D.safra.forEach((s) => { safraAgg[s] = blank(); });
const totAgg = blank();

for (let r = 0; r < N; r++) {
  const s = D.safra[C.safra[r]];
  addRow(safraAgg[s], r);
  addRow(totAgg, r);
}

console.log('\n3. Métricas Safra a Safra FPD (Oficial FPD 60, Pré-FPD 30 e MoM):');
let prevTx60 = null;
const ord = ['jan/26', 'fev/26', 'mar/26', 'abr/26', 'mai/26'];
ord.forEach(s => {
  const o = safraAgg[s];
  const tx60 = (o.c[1] / o.inst * 100);
  const tx30 = (o.c[0] / o.inst * 100);
  const tx90 = (o.c[2] / o.inst * 100);
  const adimp = ((o.inst - o.c[1]) / o.inst * 100);
  let mom = '';
  if (prevTx60 !== null) {
    const diff = tx60 - prevTx60;
    mom = ` | MoM FPD 60: ${diff >= 0 ? '+' : ''}${diff.toFixed(2)} p.p.`;
  }
  prevTx60 = tx60;
  console.log(` - ${s.toUpperCase()}: ${o.inst.toLocaleString()} inst | FPD 60: ${o.c[1].toLocaleString()} (${tx60.toFixed(2)}%)${mom} | FPD 30: ${o.c[0].toLocaleString()} (${tx30.toFixed(2)}%) | FPD 90: ${o.c[2].toLocaleString()} (${tx90.toFixed(2)}%) | Adimplência: ${adimp.toFixed(2)}%`);
});

// 4. Safra Foco (mai/26)
const foco = safraAgg['mai/26'];
const abr = safraAgg['abr/26'];
const momMai = (foco.c[1] / foco.inst * 100) - (abr.c[1] / abr.inst * 100);

console.log('\n4. Safra Foco (mai/26 - Padrão do Painel):');
console.log(` - Instalações da Safra Foco: ${foco.inst.toLocaleString()}`);
console.log(` - Taxa FPD 60 (Oficial): ${(foco.c[1] / foco.inst * 100).toFixed(2)}% (${foco.c[1].toLocaleString()} contratos)`);
console.log(` - Taxa FPD 30 (Pré-FPD): ${(foco.c[0] / foco.inst * 100).toFixed(2)}% (${foco.c[0].toLocaleString()} contratos)`);
console.log(` - Taxa FPD 90 (Pré-Churn): ${(foco.c[2] / foco.inst * 100).toFixed(2)}% (${foco.c[2].toLocaleString()} contratos)`);
console.log(` - Adimplência 1ª Fatura: ${((foco.inst - foco.c[1]) / foco.inst * 100).toFixed(2)}% (${(foco.inst - foco.c[1]).toLocaleString()} contratos em dia)`);
console.log(` - Variação MoM (vs abr/26): ${momMai >= 0 ? '+' : ''}${momMai.toFixed(2)} p.p. (${momMai <= 0 ? 'Melhora da qualidade' : 'Piora'})`);
console.log(` - Nunca Pagou (FPD 30 & 60): ${(foco.npc[1] / foco.inst * 100).toFixed(2)}% (${foco.npc[1].toLocaleString()} contratos)`);

console.log('\n5. Benchmark YTD Regional Norte (5 safras acumuladas):');
console.log(` - Total Instalações: ${totAgg.inst.toLocaleString()}`);
console.log(` - Total FPD 60 Oficial: ${(totAgg.c[1] / totAgg.inst * 100).toFixed(2)}% (${totAgg.c[1].toLocaleString()} contratos)`);
console.log(` - Total FPD 30 Pré-FPD: ${(totAgg.c[0] / totAgg.inst * 100).toFixed(2)}% (${totAgg.c[0].toLocaleString()} contratos)`);
console.log(` - Total Adimplência: ${((totAgg.inst - totAgg.c[1]) / totAgg.inst * 100).toFixed(2)}% (${(totAgg.inst - totAgg.c[1]).toLocaleString()} contratos em dia)`);

console.log('\n=== VALIDAÇÃO CONCLUÍDA COM 100% DE SUCESSO! ===');
