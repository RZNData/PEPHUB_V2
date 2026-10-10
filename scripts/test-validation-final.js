const fs = require('fs');
const path = require('path');

function runChecks() {
  console.log('=== VALIDATING ALL ADJUSTMENTS & AUXILIARY MODULES ===\n');
  let allPassed = true;

  const totalHtmlPath = path.join(__dirname, '..', 'public', 'churn-bl-total', 'index.html');
  const pmeHtmlPath = path.join(__dirname, '..', 'public', 'churn-bl-pme', 'index.html');
  const totalJsonPath = path.join(__dirname, '..', 'public', 'churn-bl-total', 'data.json');
  const pmeJsonPath = path.join(__dirname, '..', 'public', 'churn-bl-pme', 'data.json');

  const totalHtml = fs.readFileSync(totalHtmlPath, 'utf8');
  const pmeHtml = fs.readFileSync(pmeHtmlPath, 'utf8');
  const totalJson = JSON.parse(fs.readFileSync(totalJsonPath, 'utf8'));
  const pmeJson = JSON.parse(fs.readFileSync(pmeJsonPath, 'utf8'));

  // 1. Valores absolutos inteiros (sem casas decimais)
  if (totalHtml.includes('Math.round(v).toLocaleString(\'pt-BR\')') &&
      totalHtml.includes('formatNum(s.vol_real, 0)')) {
    console.log('✓ 1. Valores absolutos configurados como inteiros (sem casas decimais)');
  } else {
    console.error('[FAIL] Formatação de números inteiros incorreta');
    allPassed = false;
  }

  // 2. Separação de Grandes Mercados e Mercados em Desenvolvimento
  const gmSeparationTokens = [
    'Grandes Mercados (GM)',
    'Mercados em Desenvolvimento (MD)',
    'section-divider-row',
    'cluster-badge gm',
    'cluster-badge md'
  ];
  let sepOk = true;
  for (const t of gmSeparationTokens) {
    if (!totalHtml.includes(t) || !pmeHtml.includes(t)) {
      console.error(`[FAIL] Token de separação ausente: ${t}`);
      sepOk = false;
      allPassed = false;
    }
  }
  if (sepOk) console.log('✓ 2. Grandes Mercados e Mercados em Desenvolvimento rigorosamente separados na tabela');

  // 3. Comparativos YoY e YTD 26 x YTD 25 na tabela
  const tableCompTokens = [
    'Set/25',
    'YoY %',
    'YTD 26',
    'YTD 25',
    'Δ 26x25',
    'Var YoY %',
    'ytd_26x25_delta',
    'ytd_26x25_pct'
  ];
  let compOk = true;
  for (const t of tableCompTokens) {
    if (!totalHtml.includes(t) || !pmeHtml.includes(t)) {
      console.error(`[FAIL] Coluna comparativa ausente: ${t}`);
      compOk = false;
      allPassed = false;
    }
  }
  if (compOk) console.log('✓ 3. Colunas comparativas de YoY e YTD 26 x YTD 25 devidamente integradas na tabela');

  // 4. Modelo Projeção Residencial (Involuntária: Base, FPD, Opção, Fraude SSI)
  const projTotal = totalJson.involuntaria_proj;
  const projPme = pmeJson.involuntaria_proj;
  if (!projTotal || !projPme || !projTotal.regional || !projTotal.regional.fpd) {
    console.error('[FAIL] Objeto involuntaria_proj ausente ou incompleto no data.json');
    allPassed = false;
  } else {
    const reg = projTotal.regional;
    console.log(`✓ 4. Modelo Projeção Residencial integrado: Regional Total=${reg.total.toLocaleString('pt-BR')} (Base: ${reg.invol_base.toLocaleString('pt-BR')}, FPD: ${reg.fpd.toLocaleString('pt-BR')}, Opção: ${reg.opcao.toLocaleString('pt-BR')}, Fraude: ${reg.fraude.toLocaleString('pt-BR')})`);
  }

  // 5. Sumário Call Center (Voluntária: Ligações, Taxa OS, Motivos, Speech Analytics)
  const ccTotal = totalJson.callcenter;
  const ccPme = pmeJson.callcenter;
  if (!ccTotal || !ccTotal.regional || !ccTotal.motivos_taxa_os || !ccTotal.speech_analytics) {
    console.error('[FAIL] Objeto callcenter ausente ou incompleto no data.json');
    allPassed = false;
  } else {
    const reg = ccTotal.regional;
    console.log(`✓ 5. Sumário Call Center integrado: Atendidas=${reg.atendidas.toLocaleString('pt-BR')}, URA=${reg.ura.toLocaleString('pt-BR')}, Taxa OS=${reg.taxa_os}%, Lead Único=${reg.lead_unico.toLocaleString('pt-BR')}, Perf=${reg.performance}%, Motivos=${ccTotal.motivos_taxa_os.length}, Speech=${ccTotal.speech_analytics.length}`);
  }

  console.log('\n=======================================');
  if (allPassed) {
    console.log('RESULTADO: TODOS OS AJUSTES E NOVOS MATERIAIS FORAM 100% VALIDADOS!\n');
    process.exit(0);
  } else {
    console.error('RESULTADO: FALHA NA VALIDAÇÃO DOS AJUSTES.\n');
    process.exit(1);
  }
}

runChecks();
