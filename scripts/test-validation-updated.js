const fs = require('fs');
const path = require('path');

function runChecks() {
  console.log('=== VALIDATING NEW HISTORICAL CHARTS & CALL CENTER ENHANCEMENTS ===\n');
  let allPassed = true;

  const totalHtmlPath = path.join(__dirname, '..', 'public', 'churn-bl-total', 'index.html');
  const pmeHtmlPath = path.join(__dirname, '..', 'public', 'churn-bl-pme', 'index.html');
  const totalJsonPath = path.join(__dirname, '..', 'public', 'churn-bl-total', 'data.json');
  const pmeJsonPath = path.join(__dirname, '..', 'public', 'churn-bl-pme', 'data.json');

  const totalHtml = fs.readFileSync(totalHtmlPath, 'utf8');
  const pmeHtml = fs.readFileSync(pmeHtmlPath, 'utf8');
  const totalJson = JSON.parse(fs.readFileSync(totalJsonPath, 'utf8'));
  const pmeJson = JSON.parse(fs.readFileSync(pmeJsonPath, 'utf8'));

  // 1. Verificar histórico de 21 meses em data.json
  if (totalJson.involuntaria_proj.history.length === 21 && pmeJson.involuntaria_proj.history.length === 21) {
    console.log('✓ 1. Histórico de 21 meses do Involuntário presente em Total e PME (Jan/25 a Set/26)');
  } else {
    console.error('[FAIL] Histórico do Involuntário incompleto');
    allPassed = false;
  }

  if (totalJson.callcenter.history.length === 21 && pmeJson.callcenter.history.length === 21) {
    console.log('✓ 2. Histórico de 21 meses do Call Center presente em Total e PME (Jan/25 a Set/26)');
  } else {
    console.error('[FAIL] Histórico do Call Center incompleto');
    allPassed = false;
  }

  // 2. Verificar Matriz de Motivos com Quadro 1, Quadro 2 e Divergência
  const matrixTokens = [
    'tblCcMatriz',
    'tblCcMatrizBody',
    'Quadro 1: Participação Motivos',
    'Quadro 2: Taxa de Geração de OS',
    'Quadro 3: Divergência',
    'Diferença (Taxa OS - Mix)',
    'renderCcMatrizTable'
  ];
  for (const t of matrixTokens) {
    if (!totalHtml.includes(t) || !pmeHtml.includes(t)) {
      console.error(`[FAIL] Token da Matriz ausente: ${t}`);
      allPassed = false;
    }
  }
  console.log('✓ 3. Matriz Analítica do Call Center com Quadro 1, Quadro 2 e Divergência de letalidade integrada no HTML');

  // 3. Verificar Gráficos de Linha no Voluntário
  const ccChartsTokens = [
    'ccMotivosLineChart',
    'ccTaxaOsLineChart',
    'renderCcMotivosLineChart',
    'renderCcTaxaOsLineChart',
    'Histórico dos Motivos de Procura (% Mix de Chamadas URA)',
    'Histórico da Taxa de Geração de OS por Motivo (%)'
  ];
  for (const t of ccChartsTokens) {
    if (!totalHtml.includes(t) || !pmeHtml.includes(t)) {
      console.error(`[FAIL] Token do Gráfico de Call Center ausente: ${t}`);
      allPassed = false;
    }
  }
  console.log('✓ 4. Dois Gráficos de Linha Históricos no Voluntário (Motivos de Procura e Taxa de OS por motivo) integrados');

  // 4. Verificar Gráfico de Linha no Involuntário
  const involChartsTokens = [
    'involHistoryChart',
    'renderInvolHistoryChart',
    'Evolução Histórica das Aberturas Involuntárias (Jan/2025 a Set/2026)',
    'Involuntária Base',
    'FPD (First Payment Default)',
    'Opção (Involuntária)',
    'Fraude SSI'
  ];
  for (const t of involChartsTokens) {
    if (!totalHtml.includes(t) || !pmeHtml.includes(t)) {
      console.error(`[FAIL] Token do Gráfico do Involuntário ausente: ${t}`);
      allPassed = false;
    }
  }
  console.log('✓ 5. Gráfico de Linha Histórico das 4 Aberturas do Involuntário integrado');

  console.log('\n=======================================');
  if (allPassed) {
    console.log('RESULTADO: TODAS AS SOLICITAÇÕES FORAM ATENDIDAS E VALIDADAS COM SUCESSO!\n');
    process.exit(0);
  } else {
    console.error('RESULTADO: FALHA NA VALIDAÇÃO.\n');
    process.exit(1);
  }
}

runChecks();
