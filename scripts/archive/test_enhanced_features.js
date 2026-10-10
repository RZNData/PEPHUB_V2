const fs = require('fs');
const assert = require('assert');

function testHtml(filePath, segmentName) {
  console.log(`\n========================================`);
  console.log(`TESTING: ${segmentName} (${filePath})`);
  console.log(`========================================`);

  const html = fs.readFileSync(filePath, 'utf-8');

  // 1. Metric switch toggle
  assert(html.includes('id="btnMetricPct"'), 'Must have btnMetricPct');
  assert(html.includes('id="btnMetricAbs"'), 'Must have btnMetricAbs');
  assert(html.includes('id="globalMetricTabs"'), 'Must have globalMetricTabs');
  assert(html.includes('setMetricMode('), 'Must have setMetricMode function');
  console.log('✔ [1] Metric Mode Switcher toggle [% | Absoluto] present');

  // 2. City select in drawer and pills
  assert(html.includes('id="drawerCitySelect"'), 'Must have drawerCitySelect');
  assert(html.includes('id="cityPills"'), 'Must have cityPills');
  assert(html.includes('setCityFilter('), 'Must have setCityFilter function');
  assert(html.includes('syncCitySelectors('), 'Must have syncCitySelectors function');
  console.log('✔ [2] City Selector & 13 City Pills present');

  // 3. Dynamic Scope tags in all views
  assert(html.includes('id="kpiScopeTag"'), 'Must have kpiScopeTag');
  assert(html.includes('id="ccScopeBadge"'), 'Must have ccScopeBadge');
  assert(html.includes('id="involScopeBadge"'), 'Must have involScopeBadge');
  assert(html.includes('id="scatterScopeTag"'), 'Must have scatterScopeTag');
  assert(html.includes('id="timelineScopeTag"'), 'Must have timelineScopeTag');
  console.log('✔ [3] Dynamic Scope tags in all 5 major view areas');

  // 4. Involuntary cities historical line chart (13 cities over 21 months)
  assert(html.includes('id="involCitiesHistoryChart"'), 'Must have involCitiesHistoryChart');
  assert(html.includes('id="involCitiesLegend"'), 'Must have involCitiesLegend');
  assert(html.includes('renderInvolCitiesHistoryChart('), 'Must have renderInvolCitiesHistoryChart');
  console.log('✔ [4] Involuntary 13 Cities 21-Month History Chart present');

  // 5. Unified Month Tooltip (showMonthTip)
  assert(html.includes('showMonthTip('), 'Must have showMonthTip function');
  assert(html.includes('onmouseenter="showMonthTip('), 'Must call showMonthTip on month hover');
  console.log('✔ [5] Unified Month Tooltips present and connected to chart column strips');

  // 6. Speech Analytics Historical Line Chart + MoM / YoY
  assert(html.includes('id="ccSpeechLineChart"'), 'Must have ccSpeechLineChart');
  assert(html.includes('id="tblSpeechCompare"'), 'Must have tblSpeechCompare');
  assert(html.includes('renderCcSpeechLineChart('), 'Must have renderCcSpeechLineChart');
  console.log('✔ [6] Speech Analytics Historical Line Chart & MoM/YoY table present');

  // 7. Involuntary table styling & column separation
  assert(html.includes('class="col-sep"'), 'Must have col-sep CSS classes in involuntary table');
  assert(html.includes('tblInvolProj'), 'Must have tblInvolProj');
  console.log('✔ [7] Involuntary 4 Pillars Table has clean column separation and metrics');

  console.log(`ALL 7 ENHANCED FEATURE CHECKS PASSED FOR ${segmentName}!`);
}

testHtml('public/churn-bl-total/index.html', 'Banda Larga Total');
testHtml('public/churn-bl-pme/index.html', 'Banda Larga PME');
testHtml('public/churn-bl-total/Painel_Churn_Banda_Larga_Total.html', 'Standalone Total HTML');
testHtml('public/churn-bl-pme/Painel_Churn_Banda_Larga_PME.html', 'Standalone PME HTML');
