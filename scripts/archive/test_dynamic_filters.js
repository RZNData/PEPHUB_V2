const fs = require('fs');
const path = require('path');
const vm = require('vm');
const assert = require('assert');

function testReport(reportName, expectedValues) {
  console.log(`\n=====================================================`);
  console.log(`TESTANDO PAINEL: ${reportName}`);
  console.log(`=====================================================`);

  const htmlPath = path.resolve(__dirname, `../public/${reportName}/index.html`);
  const html = fs.readFileSync(htmlPath, 'utf8');

  assert(!html.includes('id="quickCitySelect"'), 'quickCitySelect must not exist in header');
  assert(html.includes('id="drawerCitySelect"'), 'drawerCitySelect must exist');
  assert(html.includes('data-city="BELEM"'), 'cityPills must exist');
  assert(html.includes('id="kpiScopeTag"'), 'kpiScopeTag must exist');
  console.log('✓ DOM Structure checks passed (quickCitySelect removed, drawerCitySelect, pills, scope tag)');

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
          add: () => {},
          remove: () => {},
          toggle: () => {}
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

  // 1. Regional
  context.renderAll();
  console.log('[TEST 1] Regional Norte Default:');
  console.log('  Scope:', elements['kpiScopeTag'].innerText);
  console.log('  Real:', elements['kpiReal'].innerText, `(Expected: ${expectedValues.regional.real})`);
  assert.strictEqual(elements['kpiReal'].innerText, expectedValues.regional.real);

  // 2. GM
  context.setClusterFilter('GM');
  console.log('[TEST 2] Grandes Mercados (GM):');
  console.log('  Scope:', elements['kpiScopeTag'].innerText);
  console.log('  Real:', elements['kpiReal'].innerText, `(Expected: ${expectedValues.gm.real})`);
  assert.strictEqual(elements['kpiReal'].innerText, expectedValues.gm.real);

  // 3. MD
  context.setClusterFilter('MD');
  console.log('[TEST 3] Mercados em Desenvolvimento (MD):');
  console.log('  Scope:', elements['kpiScopeTag'].innerText);
  console.log('  Real:', elements['kpiReal'].innerText, `(Expected: ${expectedValues.md.real})`);
  assert.strictEqual(elements['kpiReal'].innerText, expectedValues.md.real);

  // 4. Belém
  context.setCityFilter('BELEM');
  console.log('[TEST 4] Cidade Belém:');
  console.log('  Scope:', elements['kpiScopeTag'].innerText);
  console.log('  Real:', elements['kpiReal'].innerText, `(Expected: ${expectedValues.belem.real})`);
  assert.strictEqual(elements['kpiReal'].innerText, expectedValues.belem.real);

  // 5. Manaus
  context.setCityFilter('MANAUS');
  console.log('[TEST 5] Cidade Manaus:');
  console.log('  Scope:', elements['kpiScopeTag'].innerText);
  console.log('  Real:', elements['kpiReal'].innerText, `(Expected: ${expectedValues.manaus.real})`);
  assert.strictEqual(elements['kpiReal'].innerText, expectedValues.manaus.real);

  // 6. Reset
  context.resetAllFilters();
  console.log('[TEST 6] Reset All:');
  console.log('  Real:', elements['kpiReal'].innerText, `(Expected: ${expectedValues.regional.real})`);
  assert.strictEqual(elements['kpiReal'].innerText, expectedValues.regional.real);

  // 7. Metric switch to %
  context.setMetricMode('pct');
  console.log('[TEST 7] Modo Taxa (%):');
  console.log('  Taxa Real:', elements['kpiReal'].innerText);
  console.log('  Taxa Orç:', elements['kpiOrc'].innerText);
  assert(elements['kpiReal'].innerText.includes('%'), 'KPI Real must include % in pct mode');

  console.log(`>>> TODOS OS TESTES PASSARAM PARA ${reportName}!\n`);
}

testReport('churn-bl-total', {
  regional: { real: '9.844' },
  gm: { real: '8.658' },
  md: { real: '1.185' },
  belem: { real: '2.015' },
  manaus: { real: '4.550' }
});

testReport('churn-bl-pme', {
  regional: { real: '969' },
  gm: { real: '912' },
  md: { real: '57' },
  belem: { real: '152' },
  manaus: { real: '546' }
});
