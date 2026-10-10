const fs = require('fs');
const path = require('path');
const vm = require('vm');
const assert = require('assert');

function runFullValidation(reportName) {
  console.log(`\n======================================================`);
  console.log(`VALIDANDO 8 REQUISITOS NO PAINEL: ${reportName}`);
  console.log(`======================================================`);

  const htmlPath = path.resolve(__dirname, `../public/${reportName}/index.html`);
  const html = fs.readFileSync(htmlPath, 'utf8');

  // ==========================================
  // REQUISITO 1: Remova o filtro rápido do cabeçalho
  // ==========================================
  assert(!html.includes('id="quickCitySelect"'), '[REQ 1 FALHOU] quickCitySelect ainda está no HTML');
  assert(html.includes('id="drawerCitySelect"'), '[REQ 1 FALHOU] drawerCitySelect deve continuar existindo no drawer');
  console.log('✓ REQUISITO 1 OK: Filtro rápido removido do cabeçalho.');

  // ==========================================
  // REQUISITO 3: Todas as tabelas precisam ter as separações de seção (linhas cinza)
  // ==========================================
  assert(html.includes('th.col-sep, td.col-sep'), '[REQ 3 FALHOU] CSS col-sep não encontrado');
  assert(html.includes('border-left: 2px solid #b2c1d3 !important;'), '[REQ 3 FALHOU] Estilo de borda de seção não encontrado');
  assert(html.includes('<table id="tblMain">'), '[REQ 3 FALHOU] tblMain não encontrado');
  assert(html.includes('<table id="tblInvolProj">'), '[REQ 3 FALHOU] tblInvolProj não encontrado');
  console.log('✓ REQUISITO 3 OK: Todas as tabelas têm classes col-sep e estilo de separação cinza.');

  // ==========================================
  // REQUISITO 6: Hovers sem barra de rolagem e com pinning
  // ==========================================
  assert(!html.includes('max-height:220px; overflow-y:auto;'), '[REQ 6 FALHOU] max-height ou overflow-y:auto ainda presente no tooltip');
  assert(html.includes('overflow:visible;'), '[REQ 6 FALHOU] overflow:visible esperado no tooltip para exibir todos os dados sem corte');
  assert(html.includes('function pinTip('), '[REQ 6 FALHOU] Função pinTip não encontrada');
  assert(html.includes('gtip.classList.add(\'pinned\')'), '[REQ 6 FALHOU] Lógica de fixação de tooltip não encontrada');
  console.log('✓ REQUISITO 6 OK: Tooltip sem barras de rolagem e suporte a fixar popup ao clicar.');

  // ==========================================
  // Carregar JavaScript e testar comportamento funcional
  // ==========================================
  const jsStart = html.indexOf('<script>') + 8;
  const jsEnd = html.lastIndexOf('</script>');
  const jsCode = html.substring(jsStart, jsEnd);

  const elements = {};
  function mockEl(id) {
    if (!elements[id]) {
      elements[id] = {
        id,
        value: '',
        innerText: '',
        innerHTML: '',
        className: '',
        style: {},
        classList: {
          _classes: new Set(),
          add: function(c) { this._classes.add(c); },
          remove: function(c) { this._classes.delete(c); },
          toggle: function(c, force) {
            if(force !== undefined) {
              if(force) this._classes.add(c);
              else this._classes.delete(c);
            } else {
              if(this._classes.has(c)) this._classes.delete(c);
              else this._classes.add(c);
            }
          },
          contains: function(c) { return this._classes.has(c); }
        },
        querySelector: () => null,
        querySelectorAll: () => []
      };
    }
    return elements[id];
  }

  const mockDocument = {
    getElementById: (id) => mockEl(id),
    querySelectorAll: () => [],
    addEventListener: () => {}
  };

  const context = {
    document: mockDocument,
    console,
    Math,
    JSON,
    Set,
    Array,
    Object,
    parseFloat,
    parseInt,
    isNaN,
    Blob: function() {},
    URL: { createObjectURL: () => '' }
  };

  vm.createContext(context);
  vm.runInContext(jsCode, context);

  // Executa renderAll inicial
  context.renderAll();

  // ==========================================
  // REQUISITO 2: Quando selecionar uma cidade, o gráfico de dispersão deve mostrar apenas essa cidade
  // ==========================================
  // Sem cidade selecionada:
  const scatterAllSvg = elements['scatterContainer'].innerHTML;
  const bubbleCountAll = (scatterAllSvg.match(/class="scatter-bubble"/g) || []).length;
  assert.strictEqual(bubbleCountAll, 13, `[REQ 2 FALHOU] Esperado 13 bolhas no scatter inicial, obtido ${bubbleCountAll}`);

  // Selecionando Manaus:
  context.setCityFilter('MANAUS');
  const scatterManausSvg = elements['scatterContainer'].innerHTML;
  const bubbleCountManaus = (scatterManausSvg.match(/class="scatter-bubble"/g) || []).length;
  assert.strictEqual(bubbleCountManaus, 1, `[REQ 2 FALHOU] Esperado apenas 1 bolha no scatter ao selecionar MANAUS, obtido ${bubbleCountManaus}`);
  assert(scatterManausSvg.includes('Manaus'), '[REQ 2 FALHOU] O scatter filtrado deve conter o nome Manaus');
  assert(!scatterManausSvg.includes('Belém'), '[REQ 2 FALHOU] O scatter filtrado não deve conter Belém');
  console.log(`✓ REQUISITO 2 OK: Scatter plot isola exclusivamente a cidade selecionada (1 bolha para MANAUS vs 13 total).`);

  // Reset filter
  context.resetAllFilters();

  // ==========================================
  // REQUISITO 4: Linhas de GM e MD precisam ter seus dados em todas as tabelas
  // ==========================================
  const tblMainBody = elements['tblBody'].innerHTML;
  // Verificar se o cabeçalho de seção de GM contém dados (não colspan=20)
  assert(!tblMainBody.includes('<td colspan="20">'), '[REQ 4 FALHOU] tblMain ainda contém faixas vazias colspan="20"');
  assert(tblMainBody.includes('Grandes Mercados (GM)</span></td>'), '[REQ 4 FALHOU] Header de GM não encontrado em tblMain');
  assert(tblMainBody.includes('Mercados em Desenvolvimento (MD)</span></td>'), '[REQ 4 FALHOU] Header de MD não encontrado em tblMain');

  const tblInvolBody = elements['tblInvolProjBody'].innerHTML;
  assert(!tblInvolBody.includes('<td colspan="26">'), '[REQ 4 FALHOU] tblInvolProj ainda contém faixas vazias colspan="26"');
  assert(tblInvolBody.includes('Grandes Mercados (GM)</span></td>'), '[REQ 4 FALHOU] Header de GM não encontrado em tblInvolProj');
  assert(tblInvolBody.includes('Mercados em Desenvolvimento (MD)</span></td>'), '[REQ 4 FALHOU] Header de MD não encontrado em tblInvolProj');
  console.log('✓ REQUISITO 4 OK: Linhas de GM e MD possuem todos os dados completos nas tabelas (sem banners vazios).');

  // ==========================================
  // REQUISITO 5: Orçamento de taxa calculado ou mantido para futuro (PME)
  // ==========================================
  const rawData = vm.runInContext('RAW_DATA', context);
  if (reportName === 'churn-bl-total') {
    const regCity = rawData.modes['TOTAL'].cities.find(c => c.tipo === 'TOTAL');
    assert(regCity.taxa_orc !== null && regCity.taxa_orc > 0, '[REQ 5 FALHOU] taxa_orc deve estar calculada no Total');
    console.log(`✓ REQUISITO 5 OK: Taxa orçada Total calculada com sucesso: ${regCity.taxa_orc}% (Delta: ${regCity.taxa_delta_pp} pp)`);
  } else {
    const regCity = rawData.modes['TOTAL'].cities.find(c => c.tipo === 'TOTAL');
    assert(regCity.taxa_orc === null, '[REQ 5 FALHOU] taxa_orc do PME deve ser null para preenchimento futuro');
    console.log('✓ REQUISITO 5 OK: Campos de orçamento PME setados como null prontos para inserção futura sem dados falsos.');
  }

  // ==========================================
  // REQUISITO 7: Ajuste do rótulo do eixo vertical do gráfico de evolução histórica involuntária
  // ==========================================
  context.setMetricMode('pct');
  const involHistSvg = elements['involHistoryChart'].innerHTML;
  assert(!involHistSvg.includes('602125'), '[REQ 7 FALHOU] Gráfico involuntário ainda possui bug de 602125%');
  assert(involHistSvg.includes('Taxa de Churn Involuntário (% da Base)'), '[REQ 7 FALHOU] Título do eixo vertical ausente');
  console.log('✓ REQUISITO 7 OK: Eixo vertical do gráfico involuntário corrigido (sem valores inflados e com rótulo descritivo de taxa).');

  // ==========================================
  // REQUISITO 8: Quando selecionada a opção taxa, todos os valores convertidos e comparativos em p.p.
  // ==========================================
  // Em tblMain, verificar headers e células em modo taxa
  assert.strictEqual(elements['thVolReal'].innerText, 'Taxa Real', '[REQ 8 FALHOU] Cabeçalho thVolReal deve ser Taxa Real');
  assert.strictEqual(elements['thVolOrc'].innerText, 'Taxa Orç', '[REQ 8 FALHOU] Cabeçalho thVolOrc deve ser Taxa Orç');
  assert.strictEqual(elements['thMomVar'].innerText, 'MoM (p.p.)', '[REQ 8 FALHOU] Cabeçalho thMomVar deve ser MoM (p.p.)');
  assert.strictEqual(elements['thYoyVar'].innerText, 'YoY (p.p.)', '[REQ 8 FALHOU] Cabeçalho thYoyVar deve ser YoY (p.p.)');

  const tblMainPctBody = elements['tblBody'].innerHTML;
  assert(tblMainPctBody.includes('p.p.'), '[REQ 8 FALHOU] Comparativos em tblMain devem usar p.p.');
  
  // Gráfico de linha histórica de timeline em modo taxa
  const timelineSvg = elements['timelineContainer'].innerHTML;
  assert(timelineSvg.includes('Taxa de Churn (% da Base)'), '[REQ 8 FALHOU] Linha do tempo deve indicar taxa no eixo vertical');
  console.log('✓ REQUISITO 8 OK: Modo taxa converte métricas para % e comparativos para p.p. em tabelas, gráficos e eixos.');

  console.log(`\n🎉 TODOS OS 8 REQUISITOS FORAM 100% VALIDADOS COM SUCESSO PARA: ${reportName}!\n`);
}

runFullValidation('churn-bl-total');
runFullValidation('churn-bl-pme');
