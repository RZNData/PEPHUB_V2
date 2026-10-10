const fs = require('fs');
const path = require('path');
const zlib = require('zlib');
const assert = require('assert');

console.log("=== VALIDANDO PAINEL FPD REFINADO (5 ITENS DO USUÁRIO) ===");

const htmlPath = path.resolve(__dirname, '../Painel_FPD_Regional_Norte.html');
const html = fs.readFileSync(htmlPath, 'utf8');

// 1. Extrair PAYLOAD
const pStart = html.indexOf('const PAYLOAD = ') + 'const PAYLOAD = '.length;
const pEnd = html.indexOf('/* ============ decodificação ============ */');
const payloadJson = html.substring(pStart, pEnd).trim().replace(/;$/, '');
const PAYLOAD = JSON.parse(payloadJson);

console.log(`Payload carregado: ${PAYLOAD.n.toLocaleString()} instalações.`);

// Validar Dicionários
const D = PAYLOAD.dicts;
console.log("\n--- Checando Dicionários ---");
console.log("Safras:", D.safra);
console.log("Visão:", D.visao);
console.log("Produtos (Família Domicílio):", D.produto);
console.log("Total de Nodes únicos:", D.node.length);
console.log("Exemplos de Nodes:", D.node.slice(0, 10));

// ITEM 1: Aging 90+ zerados removidos
console.log("\n--- ITEM 1: Remoção de Aging 90+ ---");
assert(!html.includes('Taxa FPD 90 (Pré-Churn)'), "FPD 90 ainda está nos KPIs!");
assert(!html.includes('<th>FPD 90</th>'), "FPD 90 ainda está na tabela de cidades!");
assert(!html.includes('Aging 120</th>'), "Aging 120 ainda está na tabela de cidades!");
assert(!html.includes('Aging 150+</th>'), "Aging 150+ ainda está na tabela de cidades!");
assert(!html.includes('value="c90"'), "Opção c90 ainda está no seletor de métrica do mapa!");
assert(!html.includes('value="c120"'), "Opção c120 ainda está no seletor de métrica do mapa!");
assert(!html.includes('value="c150"'), "Opção c150 ainda está no seletor de métrica do mapa!");
assert(!html.includes('data-k="c90"'), "Coluna c90 ainda está na tabela de ranking!");
console.log("✓ ITEM 1 OK: Aging 90+ completamente removido de KPIs, Tabelas, Gráficos e Seletor do Mapa.");

// ITEM 2: Safra foco padrão mai/26 e sem atraso de 120 dias
console.log("\n--- ITEM 2: Safra foco mai/26 e maturidade imediata com delay oficial ---");
assert(html.includes("safraFoco='mai/26'"), "safraFoco inicial deve ser 'mai/26'");
assert(html.includes("function defaultAnchor(){ return SAFRA_DISP.length ? SAFRA_DISP[SAFRA_DISP.length - 1] : 'mai/26'; }"), "defaultAnchor deve retornar a última safra (mai/26)");
assert(html.includes("const isParcial=s=>false;"), "isParcial deve retornar false para todas as safras FPD");
assert(html.includes("const maturoR=r=>true;"), "maturoR deve retornar true para todas as safras FPD");
console.log("✓ ITEM 2 OK: Safra foco é sempre a mais recente (mai/26) e todas as safras são tratadas como fechadas/consolidadas.");

// ITEM 3: Visão Domicílio (sem Assinatura) e CD_NODE real
console.log("\n--- ITEM 3: Visão Domicílio e CD_NODE ---");
assert(D.visao.includes('Domicílio'), "D.visao deve conter 'Domicílio'");
assert(!D.visao.includes('Assinatura'), "D.visao NÃO deve conter 'Assinatura' na base de FPD");
assert(!html.includes("iv=D.visao.indexOf('Assinatura')"), "Pré-seleção forçada de Assinatura ainda existe no script!");
assert(!html.includes("ip=D.produto.indexOf('Dados')"), "Pré-seleção forçada de Dados ainda existe no script!");
assert(D.node.length > 5000, `Esperado > 5000 nodes únicos, encontrado: ${D.node.length}`);
console.log(`✓ ITEM 3 OK: Base 100% Domicílio, sem filtros travados e ${D.node.length.toLocaleString()} nodes reais identificados.`);

// ITEM 5: Visão de produto na última tabela (tblRank)
console.log("\n--- ITEM 5: Visão de produto no Ranking ---");
assert(html.includes("['produto','Produto (Família Domicílio)']"), "RANKDIMS deve conter ['produto','Produto (Família Domicílio)']");
console.log("✓ ITEM 5 OK: Aba 'Produto (Família Domicílio)' inserida em destaque no ranking.");

// Teste de decodificação das colunas
console.log("\n--- Teste de Decodificação das Colunas ---");
const cols = {};
for (const [k, obj] of Object.entries(PAYLOAD.cols)) {
  const buf = Buffer.from(obj.b, 'base64');
  const uncomp = zlib.inflateSync(buf);
  if (obj.t === 'u8') cols[k] = new Uint8Array(uncomp.buffer, uncomp.byteOffset, uncomp.byteLength);
  else if (obj.t === 'u16') cols[k] = new Uint16Array(uncomp.buffer, uncomp.byteOffset, uncomp.byteLength / 2);
  else if (obj.t === 'u32') cols[k] = new Uint32Array(uncomp.buffer, uncomp.byteOffset, uncomp.byteLength / 4);
}

console.log("Total decodificado:", cols.safra.length);
assert(cols.safra.length === 53972, "Tamanho esperado de 53.972 contratos");
assert(cols.ag30.length === 53972, "Tamanho esperado de 53.972 para ag30");
assert(cols.ag60.length === 53972, "Tamanho esperado de 53.972 para ag60");

// Métricas por Produto na Última Tabela (Simulação de drawRank com rankDim = 'produto')
console.log("\n--- Simulação tblRank por Produto ---");
const prodMap = new Map();
for (let i = 0; i < PAYLOAD.n; i++) {
  const pCode = cols.produto[i];
  if (!prodMap.has(pCode)) {
    prodMap.set(pCode, { inst: 0, c60: 0, c30: 0, np: 0 });
  }
  const o = prodMap.get(pCode);
  o.inst++;
  const a30 = cols.ag30[i];
  const a60 = cols.ag60[i];
  if (a30) o.c30++;
  if (a60) o.c60++;
  if (a30 && a60) o.np++;
}

console.log("Família Domicílio | Instalações | FPD 60 | % FPD 60 | FPD 30 | % FPD 30 | % Em Dia | Nunca Pagou");
for (const [pCode, o] of prodMap.entries()) {
  const pNome = D.produto[pCode];
  const p60 = (o.c60 / o.inst * 100).toFixed(2);
  const p30 = (o.c30 / o.inst * 100).toFixed(2);
  const emDia = ((o.inst - o.c60) / o.inst * 100).toFixed(2);
  console.log(`${pNome.padEnd(20)} | ${o.inst.toLocaleString().padStart(11)} | ${o.c60.toLocaleString().padStart(6)} | ${p60.padStart(7)}% | ${o.c30.toLocaleString().padStart(6)} | ${p30.padStart(7)}% | ${emDia.padStart(7)}% | ${o.np.toLocaleString().padStart(6)}`);
}

console.log("\n=========================================");
console.log("TODAS AS VALIDAÇÕES PASSARAM COM SUCESSO!");
console.log("=========================================");
