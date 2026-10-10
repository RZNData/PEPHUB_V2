const fs = require('fs');
const path = require('path');

function runVerification() {
  console.log('=====================================================');
  console.log('VERIFICACAO SISTEMATICA DOS 6 REQUISITOS DO USUARIO');
  console.log('=====================================================\n');

  let passed = 0;
  let failed = 0;

  function assert(condition, message) {
    if (condition) {
      console.log(`[PASS] ${message}`);
      passed++;
    } else {
      console.error(`[FAIL] ${message}`);
      failed++;
    }
  }

  // File paths
  const rootDir = path.resolve(__dirname, '..');
  const totalJsonPath = path.join(rootDir, 'public/churn-bl-total/data.json');
  const pmeJsonPath = path.join(rootDir, 'public/churn-bl-pme/data.json');
  const totalHtmlPath = path.join(rootDir, 'public/churn-bl-total/index.html');
  const pmeHtmlPath = path.join(rootDir, 'public/churn-bl-pme/index.html');
  const indexHtmlPath = path.join(rootDir, 'public/index.html');

  // STEP 1 & 2: JSON data inspection
  const totalData = JSON.parse(fs.readFileSync(totalJsonPath, 'utf8'));
  const pmeData = JSON.parse(fs.readFileSync(pmeJsonPath, 'utf8'));

  console.log('--- REQUISITO 1: Suporte a Dimensao Cidade e Mercados (GM/MD) ---');
  assert(totalData.involuntaria_proj && totalData.involuntaria_proj.regional, `BL Total invol_proj tem regional`);
  assert(totalData.involuntaria_proj && totalData.involuntaria_proj.gm, `BL Total invol_proj tem gm`);
  assert(totalData.involuntaria_proj && totalData.involuntaria_proj.md, `BL Total invol_proj tem md`);
  ['MANAUS', 'BELEM', 'SAO_LUIS', 'MACAPA', 'ANANINDEUA'].forEach(c => {
    assert(totalData.involuntaria_proj.cities[c], `BL Total invol_proj tem cidade '${c}'`);
    assert(totalData.callcenter.cities[c], `BL Total callcenter tem cidade '${c}'`);
    assert(pmeData.involuntaria_proj.cities[c], `BL PME invol_proj tem cidade '${c}'`);
    assert(pmeData.callcenter.cities[c], `BL PME callcenter tem cidade '${c}'`);
  });

  console.log('\n--- REQUISITO 2: Taxa de Churn s/ Base Realizada ---');
  assert(totalData.involuntaria_proj.regional.base_real > 400000, `BL Total base_real calculada (${totalData.involuntaria_proj.regional.base_real})`);
  assert(pmeData.involuntaria_proj.regional.base_real > 40000, `BL PME base_real calculada (${pmeData.involuntaria_proj.regional.base_real})`);
  
  assert(totalData.involuntaria_proj.regional.taxa_base !== undefined, `BL Total invol_proj tem taxa_base (${totalData.involuntaria_proj.regional.taxa_base}%)`);
  assert(totalData.involuntaria_proj.regional.taxa_fpd !== undefined, `BL Total invol_proj tem taxa_fpd (${totalData.involuntaria_proj.regional.taxa_fpd}%)`);
  assert(totalData.involuntaria_proj.regional.taxa_opcao !== undefined, `BL Total invol_proj tem taxa_opcao (${totalData.involuntaria_proj.regional.taxa_opcao}%)`);
  assert(totalData.involuntaria_proj.regional.taxa_fraude !== undefined, `BL Total invol_proj tem taxa_fraude (${totalData.involuntaria_proj.regional.taxa_fraude}%)`);
  assert(totalData.involuntaria_proj.regional.taxa_total !== undefined, `BL Total invol_proj tem taxa_total (${totalData.involuntaria_proj.regional.taxa_total}%)`);

  assert(totalData.callcenter.regional.taxa_os_base !== undefined, `BL Total Call Center tem taxa_os_base (${totalData.callcenter.regional.taxa_os_base}%)`);
  assert(totalData.callcenter.regional.motivos_matriz && totalData.callcenter.regional.motivos_matriz[0].taxa_os_base !== undefined, `BL Total Call Center matriz item tem taxa_os_base (${totalData.callcenter.regional.motivos_matriz[0].taxa_os_base}%)`);

  console.log('\n--- REQUISITO 3: Desconexao Voluntaria (Sem redundancia + Speech Historico + MoM/YoY) ---');
  const totalHtml = fs.readFileSync(totalHtmlPath, 'utf8');
  const pmeHtml = fs.readFileSync(pmeHtmlPath, 'utf8');

  assert(!totalHtml.includes('Motivos de Procura com Maior Taxa de Geração de OS (%)'), `BL Total removeu grafico redundante de motivos OS`);
  assert(!pmeHtml.includes('Motivos de Procura com Maior Taxa de Geração de OS (%)'), `BL PME removeu grafico redundante de motivos OS`);
  
  assert(totalHtml.includes('ccSpeechLineChart'), `BL Total possui container de grafico de linha historico de speech`);
  assert(pmeHtml.includes('ccSpeechLineChart'), `BL PME possui container de grafico de linha historico de speech`);
  
  assert(totalHtml.includes('tblSpeechCompare'), `BL Total possui tabela comparativa de Speech MoM e YoY/YTD`);
  assert(pmeHtml.includes('tblSpeechCompare'), `BL PME possui tabela comparativa de Speech MoM e YoY/YTD`);

  assert(totalData.callcenter.speech_analytics && totalData.callcenter.speech_analytics.length >= 8, `BL Total possui categorias de speech (${totalData.callcenter.speech_analytics.length})`);
  assert(totalData.callcenter.speech_months && totalData.callcenter.speech_months.length === 9, `BL Total possui historico de 9 meses no speech (jan/26 a set/26)`);

  console.log('\n--- REQUISITO 4: Desconexao Involuntaria (% Fraude, % Opcao, MoM e YoY) ---');
  assert(totalHtml.includes('% Participação nas Involuntárias'), `BL Total exibe Participacao % na tabela involuntaria`);
  assert(totalHtml.includes('Variação MoM vs Ago/26 (%)'), `BL Total exibe MoM % na tabela involuntaria`);
  assert(totalHtml.includes('Variação YoY vs Set/25 (%)'), `BL Total exibe YoY % na tabela involuntaria`);
  assert(totalHtml.includes('Taxa de Churn (% da Base)'), `BL Total exibe Taxa de Churn (% da Base) na tabela involuntaria`);

  assert(totalData.involuntaria_proj.regional.pct_opcao !== undefined, `BL Total tem pct_opcao (${totalData.involuntaria_proj.regional.pct_opcao}%)`);
  assert(totalData.involuntaria_proj.regional.pct_fraude !== undefined, `BL Total tem pct_fraude (${totalData.involuntaria_proj.regional.pct_fraude}%)`);
  assert(totalData.involuntaria_proj.regional.mom_opcao_pct !== undefined, `BL Total tem mom_opcao_pct (${totalData.involuntaria_proj.regional.mom_opcao_pct}%)`);
  assert(totalData.involuntaria_proj.regional.mom_fraude_pct !== undefined, `BL Total tem mom_fraude_pct (${totalData.involuntaria_proj.regional.mom_fraude_pct}%)`);
  assert(totalData.involuntaria_proj.regional.yoy_opcao_pct !== undefined, `BL Total tem yoy_opcao_pct (${totalData.involuntaria_proj.regional.yoy_opcao_pct}%)`);
  assert(totalData.involuntaria_proj.regional.yoy_fraude_pct !== undefined, `BL Total tem yoy_fraude_pct (${totalData.involuntaria_proj.regional.yoy_fraude_pct}%)`);

  console.log('\n--- REQUISITO 5: Nomenclatura Pephub - Portal de Churn & Qualidade ---');
  const indexHtml = fs.readFileSync(indexHtmlPath, 'utf8');
  assert(indexHtml.includes('Pephub — Portal de Churn & Qualidade'), `public/index.html title tem nomenclatura solicitada`);
  assert(indexHtml.includes('<b>Pephub</b> <span>Portal de Churn & Qualidade · Regional Norte</span>'), `public/index.html h1 tem nomenclatura solicitada`);
  assert(totalHtml.includes('Pephub · Churn &amp; Qualidade') || totalHtml.includes('Pephub · Churn & Qualidade'), `BL Total subheader tem nomenclatura solicitada`);
  assert(pmeHtml.includes('Pephub · Churn &amp; Qualidade') || pmeHtml.includes('Pephub · Churn & Qualidade'), `BL PME subheader tem nomenclatura solicitada`);

  console.log('\n--- REQUISITO 6: Cabecalho com Link para Home e Remocao de "Safra 28" ---');
  assert(totalHtml.includes('href="/" class="hd-btn"') && totalHtml.includes('Portal Início'), `BL Total possui link para home "/" no cabecalho`);
  assert(pmeHtml.includes('href="/" class="hd-btn"') && pmeHtml.includes('Portal Início'), `BL PME possui link para home "/" no cabecalho`);
  assert(!totalHtml.includes('Painel Safra 28'), `BL Total nao possui "Painel Safra 28" no cabecalho`);
  assert(!pmeHtml.includes('Painel Safra 28'), `BL PME nao possui "Painel Safra 28" no cabecalho`);
  assert(totalHtml.includes('href="/churn" class="hd-btn"') && totalHtml.includes('Painel Safra'), `BL Total possui link correto para Painel Safra`);
  assert(pmeHtml.includes('href="/churn" class="hd-btn"') && pmeHtml.includes('Painel Safra'), `BL PME possui link correto para Painel Safra`);

  console.log('\n=====================================================');
  console.log(`RESULTADO FINAL: ${passed} PASS, ${failed} FAIL`);
  console.log('=====================================================');

  if (failed > 0) {
    process.exit(1);
  }
}

runVerification();
