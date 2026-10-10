let currentMode = RAW_DATA.default_mode || 'TOTAL';
let clusterFilter = 'ALL';
let pickedCityId = null;
let currentMetric = 'abs'; // 'abs' (Volume) or 'pct' (Taxa)
let currentSort = { col: 'vol_real', dir: 'desc' };

/* =========================================================================
   HELP & MODAL SYSTEM
   ========================================================================= */
const HLP_CONTENT = {
  filtros: `<h4>Filtros Executivos</h4><p>Permite segmentar as praças por Grandes Mercados (GM), Mercados em Desenvolvimento (MD) ou focar numa cidade específica.</p>`,
  metrica_modo: `<h4>Modo de Visualização: % (Taxa) vs Absoluto (Volume)</h4><p><b>% (Taxa):</b> Exibe a taxa de desconexão relativa à base de clientes ativos (Volume / Base Real), permitindo comparar praças de portes diferentes com equidade.</p><p><b>Absoluto:</b> Exibe o volume nominal de desconexões (número de contratos).</p>`,
  kpis: `<h4>Síntese Executiva</h4><p>Exibe os volumes absolutos ou taxas de desconexão e comparativos percentuais de MoM, YoY e YTD.</p>`,
  callcenter: `<h4>Inteligência Call Center &amp; Retenção</h4><p>Integra o <code>Sumário Call Center S4</code> com os 6 motivos de procura na URA de retenção, taxa de OS, divergência de letalidade e evolução de 21 meses.</p>`,
  cc_motivos_hist: `<h4>Histórico dos Motivos de Procura (% Mix URA)</h4><p>Acompanha a composição das chamadas na URA de retenção ao longo de 21 meses, identificando mudanças nas demandas dos assinantes (Financeiro, Cancelamento Automático, Concorrência, etc.).</p>`,
  cc_taxa_os_hist: `<h4>Histórico da Taxa de Geração de OS</h4><p>Mede a proporção de chamadas de cada motivo que resultaram na emissão efetiva de uma ordem de cancelamento (letalidade). Quanto maior a taxa, menor a reversão/retenção pela equipe.</p>`,
  cc_matriz: `<h4>Matriz de Inteligência de Atendimento</h4><p>Cruza o volume de procura (Quadro 1) com a conversão em OS e taxa sobre a base de clientes (Quadro 2) e o diagnóstico de divergência de letalidade (Quadro 3).</p>`,
  cc_speech_hist: `<h4>Speech Analytics — Argumentos de Cancelamento</h4><p>Análise transcrita das justificativas dos clientes ao solicitar o cancelamento na URA, com evolução contínua de 9 meses e comparativos MoM (vs Ago/26) e YTD (vs Jan/26).</p>`,
  proj_invol: `<h4>Modelo Projeção Residencial (Involuntário)</h4><p>Abertura das desconexões involuntárias por Involuntária Base, FPD (1º pagamento), Opção e Fraude SSI com histórico de 21 meses.</p>`,
  invol_hist_pilares: `<h4>Evolução Histórica dos 4 Pilares Involuntários</h4><p>Mostra a evolução das componentes de desconexão involuntária: Involuntária Base (regra padrão de inadimplência), FPD (First Payment Default no 1º boleto), Opção e Fraude SSI.</p>`,
  invol_cidades: `<h4>Histórico das Cidades no Involuntário</h4><p>Apresenta a trajetória de 21 meses de desconexões involuntárias para as 13 praças monitoradas. Permite alternar entre volume e taxa sobre a base.</p>`,
  dispersao: `<h4>Dispersão MoM vs YoY</h4><p>Mapeia cada praça segundo variação mensal (MoM) e anual (YoY). Tamanho da bolha reflete o volume ou taxa de desconexões.</p>`,
  timeline: `<h4>Timeline Histórica (33 Meses)</h4><p>Evolução contínua de Janeiro de 2024 até Setembro de 2026 comparando Realizado e Orçamento.</p>`,
  tabela: `<h4>Tabela Analítica</h4><p>Apresentação das praças segregadas rigorosamente entre Grandes Mercados e Mercados em Desenvolvimento com valores absolutos e taxas.</p>`
};

function openHlp(k, e) {
  if(e) e.stopPropagation();
  const c = HLP_CONTENT[k] || '<p>Sem conteúdo de ajuda.</p>';
  document.getElementById('hlpBody').innerHTML = c;
  document.getElementById('hlpModal').classList.add('on');
}
function closeHlp() {
  document.getElementById('hlpModal').classList.remove('on');
}

/* =========================================================================
   METRIC SWITCHER (% vs Absoluto)
   ========================================================================= */
function setMetricMode(mode) {
  currentMetric = mode;
  document.querySelectorAll('.tabs button[data-m="abs"]').forEach(b => b.classList.toggle('on', mode === 'abs'));
  document.querySelectorAll('.tabs button[data-m="pct"]').forEach(b => b.classList.toggle('on', mode === 'pct'));
  updateChips();
  renderAll();
}

/* =========================================================================
   FILTER SYSTEM & SWITCHERS
   ========================================================================= */
function toggleDrawer() {
  const b = document.getElementById('drawerBody');
  const btn = document.getElementById('drawerBtn');
  const open = b.style.display !== 'none';
  b.style.display = open ? 'none' : 'block';
  btn.classList.toggle('open', !open);
}

function setDisconnectionMode(mode) {
  if(!RAW_DATA.modes[mode]) return;
  currentMode = mode;

  document.getElementById('btnModeTotal').classList.toggle('act', mode === 'TOTAL');
  document.getElementById('btnModeVol').classList.toggle('act', mode === 'VOLUNTARIA');
  document.getElementById('btnModeInvol').classList.toggle('act', mode === 'INVOLUNTARIA');

  const label = RAW_DATA.modes[mode].label;
  const badge = document.getElementById('activeModeBadge');
  badge.innerText = label;
  const accCC = document.getElementById('accCallcenter');
  const accInvol = document.getElementById('accInvoluntaria');
  if(accCC) accCC.classList.toggle('on', mode === 'VOLUNTARIA');
  if(accInvol) accInvol.classList.toggle('on', mode === 'INVOLUNTARIA');

  updateChips();
  renderAll();
}

function setClusterFilter(cluster, btn) {
  clusterFilter = cluster;
  if(btn) {
    btn.parentElement.querySelectorAll('.f-pill').forEach(b => b.classList.remove('act'));
    btn.classList.add('act');
  }
  // If picked city is not in this cluster, reset city focus
  if(pickedCityId) {
    const modeData = RAW_DATA.modes[currentMode];
    const cObj = modeData.cities.find(c => c.id === pickedCityId);
    if(cObj && cluster !== 'ALL' && cObj.grupo !== cluster) {
      pickedCityId = null;
      syncCitySelectors();
    }
  }
  updateChips();
  renderAll();
}

function syncCitySelectors() {
  const qSelect = document.getElementById('quickCitySelect');
  if(qSelect) qSelect.value = pickedCityId || '';

  const dSelect = document.getElementById('drawerCitySelect');
  if(dSelect) dSelect.value = pickedCityId || '';

  document.querySelectorAll('.city-pill').forEach(btn => {
    const cid = btn.getAttribute('data-city');
    btn.classList.toggle('act', cid === (pickedCityId || 'ALL'));
  });
}

function setCityFilter(cityId) {
  pickedCityId = (cityId && cityId.trim() !== '') ? cityId : null;
  syncCitySelectors();
  updateChips();
  renderAll();
}

function clearCityFocus() {
  setCityFilter(null);
}

function resetAllFilters() {
  clusterFilter = 'ALL';
  pickedCityId = null;
  syncCitySelectors();

  document.querySelectorAll('.filters .f-pill').forEach(b => b.classList.remove('act'));
  document.querySelectorAll('.filters .f-pills').forEach(p => {
    const first = p.querySelector('.f-pill');
    if(first) first.classList.add('act');
  });
  const pillClusterAll = document.getElementById('pillCluster_ALL');
  if(pillClusterAll) pillClusterAll.classList.add('act');

  updateChips();
  renderAll();
}

function applyFilters() {
  toggleDrawer();
}

function updateChips() {
  const modeLbl = RAW_DATA.modes[currentMode].label;
  let html = `<span class="chip">Modo: ${modeLbl}</span>`;
  html += `<span class="chip" style="font-weight:700;">Métrica: ${currentMetric === 'pct' ? 'Taxa de Churn (%)' : 'Volume Absoluto'}</span>`;

  if(clusterFilter === 'GM') html += `<span class="chip">Cluster: Grandes Mercados</span>`;
  else if(clusterFilter === 'MD') html += `<span class="chip">Cluster: Mercados em Desenvolvimento</span>`;
  else html += `<span class="chip">Cluster: Todos os Mercados</span>`;

  if(pickedCityId) {
    const modeData = RAW_DATA.modes[currentMode];
    const cObj = modeData.cities.find(c => c.id === pickedCityId);
    const name = cObj ? `${cObj.nome} (${cObj.uf})` : pickedCityId;
    html += `<span class="chip" style="background:#eaf2ec; color:#1c4b75; border-color:#c4d7e8; font-weight:700;">Praça: ${name} <a href="javascript:void(0)" onclick="clearCityFocus()" style="margin-left:4px; text-decoration:none; color:#c0392b;" title="Remover foco">×</a></span>`;
  }

  document.getElementById('chips').innerHTML = html;
}

function formatNum(v, dec = 0) {
  if(v === null || v === undefined || isNaN(v)) return '--';
  return Math.round(v).toLocaleString('pt-BR');
}

function formatPct(v) {
  if(v === null || v === undefined || isNaN(v)) return '--';
  const s = (v > 0 ? '+' : '') + v.toLocaleString('pt-BR', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + '%';
  return s;
}

function formatPp(v, dec = 2) {
  if(v === null || v === undefined || isNaN(v)) return '--';
  return (v > 0 ? '+' : '') + v.toLocaleString('pt-BR', { minimumFractionDigits: dec, maximumFractionDigits: dec }) + ' p.p.';
}

function getActiveScope() {
  const modeData = RAW_DATA.modes[currentMode];
  if(pickedCityId) {
    const cObj = modeData.cities.find(c => c.id === pickedCityId);
    const name = cObj ? cObj.nome : pickedCityId;
    const grp = cObj ? cObj.grupo : 'GM';
    return { type: 'CITY', id: pickedCityId, name: name, label: `Foco: Cidade de ${name}`, badgeClass: grp === 'GM' ? 'gm' : 'md' };
  }
  if(clusterFilter === 'GM') {
    return { type: 'GM', id: 'GM', name: 'Grandes Mercados', label: 'Foco: Grandes Mercados (6 Praças)', badgeClass: 'gm' };
  }
  if(clusterFilter === 'MD') {
    return { type: 'MD', id: 'MD', name: 'Mercados em Desenvolvimento', label: 'Foco: Mercados em Desenvolvimento (7 Praças)', badgeClass: 'md' };
  }
  return { type: 'REGIONAL', id: 'NORTE', name: 'Regional Norte', label: 'Regional Norte (Consolidado)', badgeClass: 'fe' };
}

function renderKPIs() {
  const modeData = RAW_DATA.modes[currentMode];
  let s = null;
  let scopeLabel = 'Regional Norte (Consolidado)';
  let scopeClass = 'fe';

  // 1. Specific city is picked
  if(pickedCityId) {
    const c = modeData.cities.find(x => x.id === pickedCityId);
    if(c) {
      scopeLabel = `Praça: ${c.nome} (${c.uf})`;
      scopeClass = c.grupo === 'GM' ? 'gm' : 'md';

      const totCity = RAW_DATA.modes['TOTAL'].cities.find(x => x.id === pickedCityId);
      const volCity = RAW_DATA.modes['VOLUNTARIA'].cities.find(x => x.id === pickedCityId);
      const involCity = RAW_DATA.modes['INVOLUNTARIA'].cities.find(x => x.id === pickedCityId);

      s = {
        vol_real: c.vol_real,
        vol_orc: c.vol_orc,
        rxo_delta: c.rxo_delta,
        rxo_pct: c.rxo_pct,
        mom_delta: c.mom_delta,
        mom_pct: c.mom_pct,
        vol_sep25: c.vol_sep25,
        yoy_delta: c.yoy_delta,
        yoy_pct: c.yoy_pct,
        ytd_real: c.ytd_real,
        ytd_orc: c.ytd_orc,
        ytd_rxo_delta: c.ytd_rxo_delta,
        ytd_rxo_pct: c.ytd_rxo_pct,
        ytd_2025: c.ytd_2025,
        ytd_26x25_delta: c.ytd_26x25_delta,
        ytd_26x25_pct: c.ytd_26x25_pct,
        base_real: c.base_real,
        base_orc: c.base_orc,
        taxa_real: c.taxa_real,
        taxa_orc: c.taxa_orc,
        taxa_delta_pp: c.taxa_delta_pp !== undefined ? c.taxa_delta_pp : (c.taxa_real - c.taxa_orc),
        taxa_mom_pp: c.taxa_mom_pp,
        taxa_yoy_pp: c.taxa_yoy_pp,
        badge_total: totCity ? totCity.vol_real : c.vol_real,
        badge_vol: volCity ? volCity.vol_real : 0,
        badge_invol: involCity ? involCity.vol_real : 0
      };
    }
  }

  // 2. Filtered by GM cluster
  if(!s && clusterFilter === 'GM') {
    const sub = modeData.cities.find(c => c.id === 'GM' && c.tipo === 'SUBTOTAL');
    if(sub) {
      scopeLabel = 'Grandes Mercados (GM · 6 Praças)';
      scopeClass = 'gm';
      const totSub = RAW_DATA.modes['TOTAL'].cities.find(c => c.id === 'GM' && c.tipo === 'SUBTOTAL');
      const volSub = RAW_DATA.modes['VOLUNTARIA'].cities.find(c => c.id === 'GM' && c.tipo === 'SUBTOTAL');
      const involSub = RAW_DATA.modes['INVOLUNTARIA'].cities.find(c => c.id === 'GM' && c.tipo === 'SUBTOTAL');
      s = {
        ...sub,
        badge_total: totSub ? totSub.vol_real : sub.vol_real,
        badge_vol: volSub ? volSub.vol_real : 0,
        badge_invol: involSub ? involSub.vol_real : 0
      };
    }
  }

  // 3. Filtered by MD cluster
  if(!s && clusterFilter === 'MD') {
    const sub = modeData.cities.find(c => c.id === 'MD' && c.tipo === 'SUBTOTAL');
    if(sub) {
      scopeLabel = 'Mercados em Desenvolvimento (MD · 7 Praças)';
      scopeClass = 'md';
      const totSub = RAW_DATA.modes['TOTAL'].cities.find(c => c.id === 'MD' && c.tipo === 'SUBTOTAL');
      const volSub = RAW_DATA.modes['VOLUNTARIA'].cities.find(c => c.id === 'MD' && c.tipo === 'SUBTOTAL');
      const involSub = RAW_DATA.modes['INVOLUNTARIA'].cities.find(c => c.id === 'MD' && c.tipo === 'SUBTOTAL');
      s = {
        ...sub,
        badge_total: totSub ? totSub.vol_real : sub.vol_real,
        badge_vol: volSub ? volSub.vol_real : 0,
        badge_invol: involSub ? involSub.vol_real : 0
      };
    }
  }

  // 4. Default Regional (ALL)
  if(!s) {
    s = {
      ...modeData.summary,
      badge_total: RAW_DATA.modes['TOTAL'].summary.vol_real,
      badge_vol: RAW_DATA.modes['VOLUNTARIA'].summary.vol_real,
      badge_invol: RAW_DATA.modes['INVOLUNTARIA'].summary.vol_real
    };
  }

  // Update executive scope tag
  const tag = document.getElementById('kpiScopeTag');
  if(tag) {
    tag.className = `tag ${scopeClass}`;
    tag.innerText = scopeLabel;
  }

  // Populate cards based on active metric (% vs Absoluto)
  const isPct = (currentMetric === 'pct');
  const baseReal = s.base_real || 1;
  const baseOrc = s.base_orc || 1;

  if(isPct) {
    document.getElementById('kpiReal').innerText = s.taxa_real ? s.taxa_real.toLocaleString('pt-BR', {minimumFractionDigits:2, maximumFractionDigits:2}) + '%' : '--';
    const momPp = s.taxa_mom_pp !== undefined ? s.taxa_mom_pp : ((s.taxa_real || 0) - ((s.vol_real - (s.mom_delta || 0)) / baseReal * 100));
    const momSign = momPp < 0 ? 'tag fe' : 'tag crit';
    document.getElementById('kpiMomDelta').innerHTML = `MoM: <span class="${momSign}">${formatPp(momPp, 2)}</span> · Base: <b>${formatNum(baseReal, 0)}</b>`;

    document.getElementById('kpiOrc').innerText = s.taxa_orc ? s.taxa_orc.toLocaleString('pt-BR', {minimumFractionDigits:2, maximumFractionDigits:2}) + '%' : '--';
    document.getElementById('kpiOrcBaseNote').innerHTML = s.base_orc ? (`Base Orçada: <b>${formatNum(s.base_orc, 0)}</b>`) : 'Taxa Orçada';

    const taxaPpClass = (s.taxa_delta_pp || 0) <= 0 ? 'tag fe' : 'tag crit';
    document.getElementById('kpiRxo').innerText = formatPp(s.taxa_delta_pp, 2);
    document.getElementById('kpiRxoPct').innerHTML = `<span class="${taxaPpClass}">Desvio vs Orçamento (p.p.)</span>`;

    document.getElementById('kpiYtdReal').innerText = s.taxa_real ? s.taxa_real.toFixed(2) + '%' : '--';
    document.getElementById('kpiYtdOrc').innerText = s.taxa_orc ? s.taxa_orc.toFixed(2) + '%' : '--';
    document.getElementById('kpiYtdRxo').innerText = formatPp(s.taxa_delta_pp, 2);
    document.getElementById('kpiYtdRxoPct').innerHTML = `<span class="${taxaPpClass}">Desvio vs Orçado (p.p.)</span>`;

    const yoyPp = s.taxa_yoy_pp !== undefined ? s.taxa_yoy_pp : ((s.taxa_real || 0) - ((s.vol_sep25 || 0) / (baseReal || 1) * 100));
    const yoySign = yoyPp <= 0 ? 'tag fe' : 'tag crit';
    document.getElementById('kpiYtdYoy').innerHTML = `<span class="${yoySign}">${formatPp(yoyPp, 2)}</span>`;
    const taxaSep25 = (s.vol_sep25 / (baseReal || 1)) * 100;
    document.getElementById('kpiYtd25').innerText = `vs Set/25 (${taxaSep25.toFixed(2)}%)`;
  } else {
    document.getElementById('kpiReal').innerText = formatNum(s.vol_real, 0);
    const momSign = s.mom_pct < 0 ? 'tag fe' : 'tag crit';
    document.getElementById('kpiMomDelta').innerHTML = `MoM: <span class="${momSign}">${formatPct(s.mom_pct)}</span> (${s.mom_delta > 0 ? '+' : ''}${formatNum(s.mom_delta, 0)})`;

    document.getElementById('kpiOrc').innerText = formatNum(s.vol_orc, 0);
    document.getElementById('kpiOrcBaseNote').innerText = 'Desafio Orçamentário';

    document.getElementById('kpiRxo').innerText = (s.rxo_delta > 0 ? '+' : '') + formatNum(s.rxo_delta, 0);
    const rxoClass = s.rxo_delta <= 0 ? 'tag fe' : 'tag ab';
    document.getElementById('kpiRxoPct').innerHTML = `<span class="${rxoClass}">${formatPct(s.rxo_pct)} vs Orçado</span>`;

    document.getElementById('kpiYtdReal').innerText = formatNum(s.ytd_real, 0);
    document.getElementById('kpiYtdOrc').innerText = formatNum(s.ytd_orc, 0);
    document.getElementById('kpiYtdRxo').innerText = (s.ytd_rxo_delta > 0 ? '+' : '') + formatNum(s.ytd_rxo_delta, 0);
    const ytdRxoClass = (s.ytd_rxo_delta || 0) <= 0 ? 'tag fe' : 'tag ab';
    document.getElementById('kpiYtdRxoPct').innerHTML = `<span class="${ytdRxoClass}">${formatPct(s.ytd_rxo_pct)} vs Orçado</span>`;

    const ytd26x25Sign = (s.ytd_26x25_pct || 0) <= 0 ? 'tag fe' : 'tag crit';
    document.getElementById('kpiYtdYoy').innerHTML = `<span class="${ytd26x25Sign}">${formatPct(s.ytd_26x25_pct)}</span>`;
    document.getElementById('kpiYtd25').innerText = `vs YTD 2025 (${formatNum(s.ytd_2025, 0)} | ${s.ytd_26x25_delta > 0 ? '+' : ''}${formatNum(s.ytd_26x25_delta, 0)})`;
  }

  document.getElementById('kpiTaxa').innerText = s.taxa_real ? s.taxa_real.toLocaleString('pt-BR', {minimumFractionDigits:2, maximumFractionDigits:2}) + '%' : '--';
  const taxaPpClass = (s.taxa_delta_pp || 0) <= 0 ? 'tag fe' : 'tag crit';
  document.getElementById('kpiTaxaDelta').innerHTML = `Orçado: ${s.taxa_orc ? s.taxa_orc.toLocaleString('pt-BR', {minimumFractionDigits:2, maximumFractionDigits:2}) : '--'}% (<span class="${taxaPpClass}">${formatPp(s.taxa_delta_pp, 2)}</span>)`;

  // Update mode switcher badges to reflect active metric mode and scope!
  if(isPct && baseReal > 0) {
    document.getElementById('badgeVolTotal').innerText = ((s.badge_total / baseReal) * 100).toFixed(2) + '%';
    document.getElementById('badgeVolVol').innerText = ((s.badge_vol / baseReal) * 100).toFixed(2) + '%';
    document.getElementById('badgeVolInvol').innerText = ((s.badge_invol / baseReal) * 100).toFixed(2) + '%';
  } else {
    document.getElementById('badgeVolTotal').innerText = formatNum(s.badge_total, 0);
    document.getElementById('badgeVolVol').innerText = formatNum(s.badge_vol, 0);
    document.getElementById('badgeVolInvol').innerText = formatNum(s.badge_invol, 0);
  }
}

/* =========================================================================
   HISTORICAL LINE CHART: MOTIVOS DE PROCURA (% MIX · Jan/25 a Set/26)
   ========================================================================= */
function renderCcMotivosLineChart(curCC) {
  const container = document.getElementById('ccMotivosLineChart');
  if(!container) return;
  const cc = RAW_DATA.callcenter;
  if(!cc) return;

  const pts = (curCC && curCC.history) ? curCC.history : cc.history;
  if(!pts || pts.length === 0) return;

  const W = 800, H = 250;
  const padL = 45, padR = 25, padT = 20, padB = 35;
  const plotW = W - padL - padR;
  const plotH = H - padT - padB;

  const motives = [
    { id: 'financeiro', name: 'Financeiro', color: '#2a5d8f' },
    { id: 'canc_auto', name: 'Canc. Automático', color: '#c0392b' },
    { id: 'concorrencia', name: 'Concorrência', color: '#c98a15' },
    { id: 'me', name: 'Mudança de Endereço', color: '#8a0f18' },
    { id: 'tecnico', name: 'Técnico', color: '#516173' },
    { id: 'atendimento', name: 'Atendimento', color: '#6b4b8a' }
  ];

  const maxY = 55;
  const getX = i => padL + (i / (pts.length - 1)) * plotW;
  const getY = v => padT + (1 - (Math.min(maxY, Math.max(0, v)) / maxY)) * plotH;

  let svg = `<svg class="chart-svg" viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg">`;

  [0, 10, 20, 30, 40, 50].forEach(val => {
    const y = getY(val);
    svg += `<line x1="${padL}" y1="${y}" x2="${padL + plotW}" y2="${y}" stroke="#eceef1" stroke-width="1" />`;
    svg += `<text x="${padL - 6}" y="${y + 3.5}" fill="#8b95a3" font-size="9.5" text-anchor="end">${val}%</text>`;
  });

  motives.forEach(m => {
    let lineD = '';
    pts.forEach((p, i) => {
      const val = p.mix[m.id];
      if(val !== undefined && val !== null) {
        lineD += ` ${lineD === '' ? 'M' : 'L'} ${getX(i)} ${getY(val)}`;
      }
    });
    svg += `<path d="${lineD}" fill="none" stroke="${m.color}" stroke-width="2" opacity="0.9" />`;
  });

  pts.forEach((p, i) => {
    const x = getX(i);
    if(i % 3 === 0 || i === pts.length - 1) {
      svg += `<text x="${x}" y="${padT + plotH + 16}" fill="#8b95a3" font-size="9" text-anchor="middle">${p.label}</text>`;
      svg += `<line x1="${x}" y1="${padT + plotH}" x2="${x}" y2="${padT + plotH + 3}" stroke="#dfe3e8" stroke-width="1" />`;
    }

    motives.forEach(m => {
      const val = p.mix[m.id];
      if(val !== undefined && val !== null) {
        const y = getY(val);
        const isLast = (i === pts.length - 1);
        svg += `<circle cx="${x}" cy="${y}" r="${isLast ? 4 : 2.5}" fill="${m.color}" stroke="#fff" stroke-width="1" />`;
      }
    });

    // Unified Month Tooltip (Requisito 3)
    const monthItems = motives.map(m => {
      const val = p.mix[m.id] || 0;
      return {
        label: m.name,
        val: `${val.toFixed(1)}%`,
        color: m.color,
        numVal: val
      };
    }).sort((a, b) => b.numVal - a.numVal);

    const monthTipData = JSON.stringify({
      title: `📅 ${p.label} · Motivos de Procura URA`,
      subtitle: `Mix de Chamadas na Retenção`,
      items: monthItems,
      footer: `Participação percentual no total de atendimentos`
    }).replace(/"/g, '&quot;');

    const stepW = plotW / (pts.length - 1);
    svg += `<rect x="${x - stepW / 2}" y="${padT}" width="${stepW}" height="${plotH}" fill="transparent"
                 style="cursor:pointer;"
                 onclick="pinTip(event, '${monthTipData}')"
                 onmouseenter="showMonthTip(event, '${monthTipData}')"
                 onmousemove="positionTip(event)"
                 onmouseleave="hideTip()" />`;
  });

  svg += `</svg>`;
  container.innerHTML = svg;
}

/* =========================================================================
   HISTORICAL LINE CHART: TAXA DE OS POR MOTIVO (% · Jan/25 a Set/26)
   ========================================================================= */
function renderCcTaxaOsLineChart(curCC) {
  const container = document.getElementById('ccTaxaOsLineChart');
  if(!container) return;
  const cc = RAW_DATA.callcenter;
  if(!cc) return;

  const pts = (curCC && curCC.history) ? curCC.history : cc.history;
  if(!pts || pts.length === 0) return;

  const W = 800, H = 250;
  const padL = 45, padR = 25, padT = 20, padB = 35;
  const plotW = W - padL - padR;
  const plotH = H - padT - padB;

  const motives = [
    { id: 'me', name: 'Mudança de Endereço', color: '#8a0f18' },
    { id: 'canc_auto', name: 'Canc. Automático', color: '#c0392b' },
    { id: 'tecnico', name: 'Técnico', color: '#516173' },
    { id: 'concorrencia', name: 'Concorrência', color: '#c98a15' },
    { id: 'atendimento', name: 'Atendimento', color: '#6b4b8a' },
    { id: 'financeiro', name: 'Financeiro', color: '#2a5d8f' }
  ];

  const maxY = 45;
  const getX = i => padL + (i / (pts.length - 1)) * plotW;
  const getY = v => padT + (1 - (Math.min(maxY, Math.max(0, v)) / maxY)) * plotH;

  let svg = `<svg class="chart-svg" viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg">`;

  [0, 10, 20, 30, 40].forEach(val => {
    const y = getY(val);
    svg += `<line x1="${padL}" y1="${y}" x2="${padL + plotW}" y2="${y}" stroke="#eceef1" stroke-width="1" />`;
    svg += `<text x="${padL - 6}" y="${y + 3.5}" fill="#8b95a3" font-size="9.5" text-anchor="end">${val}%</text>`;
  });

  motives.forEach(m => {
    let lineD = '';
    pts.forEach((p, i) => {
      const val = p.taxa_os[m.id];
      if(val !== undefined && val !== null) {
        lineD += ` ${lineD === '' ? 'M' : 'L'} ${getX(i)} ${getY(val)}`;
      }
    });
    svg += `<path d="${lineD}" fill="none" stroke="${m.color}" stroke-width="${m.id === 'me' ? '2.5' : '1.8'}" opacity="0.9" />`;
  });

  pts.forEach((p, i) => {
    const x = getX(i);
    if(i % 3 === 0 || i === pts.length - 1) {
      svg += `<text x="${x}" y="${padT + plotH + 16}" fill="#8b95a3" font-size="9" text-anchor="middle">${p.label}</text>`;
      svg += `<line x1="${x}" y1="${padT + plotH}" x2="${x}" y2="${padT + plotH + 3}" stroke="#dfe3e8" stroke-width="1" />`;
    }

    motives.forEach(m => {
      const val = p.taxa_os[m.id];
      if(val !== undefined && val !== null) {
        const y = getY(val);
        const isLast = (i === pts.length - 1);
        svg += `<circle cx="${x}" cy="${y}" r="${isLast ? 4 : 2.5}" fill="${m.color}" stroke="#fff" stroke-width="1" />`;
      }
    });

    // Unified Month Tooltip (Requisito 3)
    const monthItems = motives.map(m => {
      const val = p.taxa_os[m.id] || 0;
      return {
        label: m.name,
        val: `${val.toFixed(1)}%`,
        color: m.color,
        note: `(Retenção: ${ (100 - val).toFixed(1) }%)`,
        numVal: val
      };
    }).sort((a, b) => b.numVal - a.numVal);

    const monthTipData = JSON.stringify({
      title: `📅 ${p.label} · Taxa de Conversão em OS`,
      subtitle: `Percentual de ligações convertidas em cancelamento`,
      items: monthItems,
      footer: `Conversão URA Retenção em Ordem de Cancelamento`
    }).replace(/"/g, '&quot;');

    const stepW = plotW / (pts.length - 1);
    svg += `<rect x="${x - stepW / 2}" y="${padT}" width="${stepW}" height="${plotH}" fill="transparent"
                 style="cursor:pointer;"
                 onclick="pinTip(event, '${monthTipData}')"
                 onmouseenter="showMonthTip(event, '${monthTipData}')"
                 onmousemove="positionTip(event)"
                 onmouseleave="hideTip()" />`;
  });

  svg += `</svg>`;
  container.innerHTML = svg;
}

/* =========================================================================
   MATRIZ ANALÍTICA: PARTICIPAÇÃO (Q1) vs TAXA DE OS & TAXA S/ BASE (Q2) & DIVERGÊNCIA
   ========================================================================= */
function renderCcMatrizTable(curCC) {
  const tbody = document.getElementById('tblCcMatrizBody');
  if(!tbody) return;
  const cc = RAW_DATA.callcenter;
  if(!cc) return;

  const matriz = (curCC && curCC.motivos_matriz) ? curCC.motivos_matriz : cc.motivos_matriz;
  if(!matriz) return;

  let html = '';
  let totCalls = 0;
  let totOs = 0;
  const baseReal = (curCC && curCC.base_real) ? curCC.base_real : (cc.regional ? cc.regional.base_real : 1);

  matriz.forEach(m => {
    totCalls += m.ligacoes;
    totOs += m.os_geradas;

    const divPp = m.divergencia_pp;
    const divClass = divPp > 15 ? 'tag crit' : (divPp > 0 ? 'tag ab' : 'tag fe');
    const divSign = divPp > 0 ? '+' : '';

    const momMixSign = m.mix_mom_pp < 0 ? 'color:var(--green);font-weight:600;' : 'color:var(--red);font-weight:600;';
    const yoyMixSign = m.mix_yoy_pp < 0 ? 'color:var(--green);font-weight:600;' : 'color:var(--red);font-weight:600;';

    const momTxSign = m.taxa_os_mom_pp < 0 ? 'color:var(--green);font-weight:600;' : 'color:var(--red);font-weight:600;';
    const yoyTxSign = m.taxa_os_yoy_pp < 0 ? 'color:var(--green);font-weight:600;' : 'color:var(--red);font-weight:600;';

    const statusTag = m.status === 'Crítico' ? 'tag crit' : (m.status === 'Alto' ? 'tag ab' : (m.status === 'Controlado' ? 'tag fe' : 'tag'));
    const txBaseVal = m.taxa_os_base !== undefined ? m.taxa_os_base : (baseReal > 0 ? ((m.os_geradas / baseReal) * 100).toFixed(2) : '--');

    html += `<tr>
      <td class="l" style="font-weight:700;">
        <span style="display:inline-block; width:9px; height:9px; border-radius:50%; background:${m.color || '#2a5d8f'}; margin-right:6px; vertical-align:-1px;"></span>
        ${m.motivo}
      </td>
      <td class="col-sep">${formatNum(m.ligacoes, 0)}</td>
      <td style="font-weight:700; color:var(--blue);">${m.mix_pct}%</td>
      <td style="font-size:11px;">
        <span style="${momMixSign}">${m.mix_mom_pp > 0 ? '+' : ''}${m.mix_mom_pp} pp</span> / 
        <span style="${yoyMixSign}">${m.mix_yoy_pp > 0 ? '+' : ''}${m.mix_yoy_pp} pp</span>
      </td>
      <td class="col-sep">${formatNum(m.os_geradas, 0)}</td>
      <td style="font-weight:700; color:var(--red); font-size:12.5px;">${m.taxa_os_pct}%</td>
      <td style="color:var(--green); font-weight:700;">${m.taxa_retencao_pct}%</td>
      <td style="color:var(--ink); font-weight:700;">${txBaseVal}%</td>
      <td style="font-size:11px;">
        <span style="${momTxSign}">${m.taxa_os_mom_pp > 0 ? '+' : ''}${m.taxa_os_mom_pp} pp</span> / 
        <span style="${yoyTxSign}">${m.taxa_os_yoy_pp > 0 ? '+' : ''}${m.taxa_os_yoy_pp} pp</span>
      </td>
      <td class="col-sep">
        <span class="${divClass}" style="font-size:11px; font-weight:700;">${divSign}${divPp} p.p.</span>
      </td>
      <td class="l" style="font-size:11.5px; color:var(--ink2);">${m.dinamica}</td>
      <td><span class="${statusTag}">${m.status}</span></td>
    </tr>`;
  });

  const overallTxOs = totCalls > 0 ? ((totOs / totCalls) * 100).toFixed(1) : '0';
  const overallRet = (100 - parseFloat(overallTxOs)).toFixed(1);
  const overallTxBase = baseReal > 0 ? ((totOs / baseReal) * 100).toFixed(2) : '--';
  html += `<tr style="background:#f0f3f6; font-weight:800; border-top:2px solid var(--line);">
    <td class="l">TOTAL URA RETENÇÃO</td>
    <td class="col-sep">${formatNum(totCalls, 0)}</td>
    <td>100,0%</td>
    <td>--</td>
    <td class="col-sep">${formatNum(totOs, 0)}</td>
    <td style="color:var(--red); font-size:13px;">${overallTxOs}%</td>
    <td style="color:var(--green); font-size:13px;">${overallRet}%</td>
    <td style="color:var(--ink); font-size:13px;">${overallTxBase}%</td>
    <td>--</td>
    <td class="col-sep"><span class="tag">0,0 p.p.</span></td>
    <td class="l" style="font-size:11px; color:var(--ink2);">Consolidado dos 6 Motivos Auditados</td>
    <td><span class="tag fe">Ativo</span></td>
  </tr>`;

  tbody.innerHTML = html;
}

/* =========================================================================
   HISTORICAL LINE CHART & COMPARE TABLE: SPEECH ANALYTICS (Jan/26 a Set/26)
   ========================================================================= */
function renderCcSpeechLineChart(curCC) {
  const container = document.getElementById('ccSpeechLineChart');
  const legendBox = document.getElementById('ccSpeechLegend');
  const tbody = document.getElementById('tblSpeechCompareBody');
  if(!container || !tbody) return;

  const cc = RAW_DATA.callcenter;
  if(!cc) return;

  const sHistory = (curCC && curCC.speech_history) ? curCC.speech_history : cc.speech_history;
  const sAnalytics = (curCC && curCC.speech_analytics) ? curCC.speech_analytics : cc.speech_analytics;
  const catsMeta = cc.speech_cats_meta || [
    { id: 'acha_caro', speech: 'Acha Caro / Aumento no Valor', color: '#c98a15' },
    { id: 'reajuste', speech: 'Reajuste / Aumento de Valor', color: '#e67e22' },
    { id: 'pouca_util', speech: 'Sem / Pouca Utilização', color: '#7f8c8d' },
    { id: 'nao_pedi', speech: 'Não Pedi / Solicitei', color: '#95a5a6' },
    { id: 'tecnico', speech: 'Técnico - Internet', color: '#2980b9' },
    { id: 'concorrencia', speech: 'Concorrência', color: '#f39c12' },
    { id: 'financeiro', speech: 'Dificuldade Financeira / Reclama do Valor', color: '#16a085' },
    { id: 'consulta_val', speech: 'Não Concorda e/ou Consulta Valores', color: '#8e44ad' },
    { id: 'mudanca_end', speech: 'Mudança de Endereço', color: '#c0392b' }
  ];

  if(!sHistory || sHistory.length === 0) return;

  // Render Legend
  if(legendBox) {
    let legHtml = '';
    catsMeta.forEach(c => {
      legHtml += `<span><i style="background:${c.color}; border-radius:50%;"></i>${c.speech.split('/')[0].trim()}</span>`;
    });
    legendBox.innerHTML = legHtml;
  }

  // Render SVG Line Chart
  const W = 700, H = 280;
  const padL = 40, padR = 25, padT = 20, padB = 35;
  const plotW = W - padL - padR;
  const plotH = H - padT - padB;

  let maxVal = 0;
  sHistory.forEach(pt => {
    catsMeta.forEach(c => {
      const v = pt[c.id] || 0;
      if(v > maxVal) maxVal = v;
    });
  });
  maxVal = Math.max(16, Math.ceil(maxVal / 5) * 5 + 2);

  const getX = i => padL + (i / (sHistory.length - 1)) * plotW;
  const getY = v => padT + (1 - (Math.min(maxVal, Math.max(0, v)) / maxVal)) * plotH;

  let svg = `<svg class="chart-svg" viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg">`;

  // Grid
  [0, 5, 10, 15, 20, 25].forEach(val => {
    if(val <= maxVal) {
      const y = getY(val);
      svg += `<line x1="${padL}" y1="${y}" x2="${padL + plotW}" y2="${y}" stroke="#eceef1" stroke-width="1" />`;
      svg += `<text x="${padL - 6}" y="${y + 3.5}" fill="#8b95a3" font-size="9" text-anchor="end">${val}%</text>`;
    }
  });

  // Lines
  catsMeta.forEach(c => {
    let lineD = '';
    sHistory.forEach((pt, i) => {
      const val = pt[c.id];
      if(val !== undefined && val !== null) {
        lineD += ` ${lineD === '' ? 'M' : 'L'} ${getX(i)} ${getY(val)}`;
      }
    });
    svg += `<path d="${lineD}" fill="none" stroke="${c.color}" stroke-width="1.8" opacity="0.92" />`;
  });

  // Points & unified month tooltips
  sHistory.forEach((pt, i) => {
    const x = getX(i);
    if(i % 3 === 0 || i === sHistory.length - 1) {
      svg += `<text x="${x}" y="${padT + plotH + 16}" fill="#8b95a3" font-size="9" text-anchor="middle">${pt.label}</text>`;
      svg += `<line x1="${x}" y1="${padT + plotH}" x2="${x}" y2="${padT + plotH + 3}" stroke="#dfe3e8" stroke-width="1" />`;
    }

    catsMeta.forEach(c => {
      const val = pt[c.id];
      if(val !== undefined && val !== null) {
        const y = getY(val);
        const isLast = (i === sHistory.length - 1);
        svg += `<circle cx="${x}" cy="${y}" r="${isLast ? 4 : 2.5}" fill="${c.color}" stroke="#fff" stroke-width="1" />`;
      }
    });

    // Unified Month Tooltip (Requisito 3)
    const monthItems = catsMeta.map(c => {
      const val = pt[c.id] || 0;
      return {
        label: c.speech.split('/')[0].trim(),
        val: `${val.toFixed(1)}%`,
        color: c.color,
        numVal: val
      };
    }).sort((a, b) => b.numVal - a.numVal);

    const monthTipData = JSON.stringify({
      title: `📅 ${pt.label} · Speech Analytics Cancelamento`,
      subtitle: `Mix de Menções nos Motivos Declarados`,
      items: monthItems,
      footer: `Categorização automática de chamadas de cancelamento`
    }).replace(/"/g, '&quot;');

    const stepW = plotW / (sHistory.length - 1);
    svg += `<rect x="${x - stepW / 2}" y="${padT}" width="${stepW}" height="${plotH}" fill="transparent"
                 style="cursor:pointer;"
                 onclick="pinTip(event, '${monthTipData}')"
                 onmouseenter="showMonthTip(event, '${monthTipData}')"
                 onmousemove="positionTip(event)"
                 onmouseleave="hideTip()" />`;
  });

  svg += `</svg>`;
  container.innerHTML = svg;

  // Render Comparative Table
  let tHtml = '';
  const sortedAnalytics = [...sAnalytics].sort((a, b) => b.pct - a.pct);
  sortedAnalytics.forEach(item => {
    const momColor = item.mom_pp > 0 ? 'color:var(--red); font-weight:700;' : (item.mom_pp < 0 ? 'color:var(--green); font-weight:700;' : 'color:var(--ink3);');
    const ytdColor = item.ytd_pp > 0 ? 'color:var(--red); font-weight:700;' : (item.ytd_pp < 0 ? 'color:var(--green); font-weight:700;' : 'color:var(--ink3);');
    const tagClass = item.mom_pp > 0.3 ? 'tag crit' : (item.mom_pp < -0.3 ? 'tag fe' : 'tag');

    tHtml += `<tr>
      <td class="l" style="font-weight:600;">
        <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:${item.color}; margin-right:6px; vertical-align:-1px;"></span>
        ${item.speech}
      </td>
      <td style="font-weight:700; font-size:12px;">${item.pct.toFixed(1)}%</td>
      <td style="${momColor}">${item.mom_pp > 0 ? '+' : ''}${item.mom_pp.toFixed(1)} pp</td>
      <td style="${ytdColor}">${item.ytd_pp > 0 ? '+' : ''}${item.ytd_pp.toFixed(1)} pp</td>
      <td><span class="${tagClass}">${item.tendencia}</span></td>
    </tr>`;
  });
  tbody.innerHTML = tHtml;
}

/* =========================================================================
   ACESSÓRIO: CALL CENTER (Desconexão Voluntária)
   ========================================================================= */
function renderCallcenterModule() {
  const cc = RAW_DATA.callcenter;
  if(!cc) return;
  const scope = getActiveScope();

  const scopeBadge = document.getElementById('ccScopeBadge');
  if(scopeBadge) {
    scopeBadge.className = `tag ${scope.badgeClass}`;
    scopeBadge.innerText = scope.label;
  }

  let curCC = cc.regional;
  if(scope.type === 'CITY' && cc.cities && cc.cities[scope.id]) curCC = cc.cities[scope.id];
  else if(scope.type === 'GM' && cc.gm) curCC = cc.gm;
  else if(scope.type === 'MD' && cc.md) curCC = cc.md;

  document.getElementById('ccAtend').innerText = formatNum(curCC.atendidas, 0);
  document.getElementById('ccUnicas').innerText = `${formatNum(curCC.unicas, 0)} chamadas únicas`;
  document.getElementById('ccUra').innerText = formatNum(curCC.ura, 0);
  document.getElementById('ccMix').innerText = `${curCC.mix_ura}% do mix total`;
  document.getElementById('ccTxOs').innerText = `${curCC.taxa_os}%`;
  document.getElementById('ccLead').innerText = formatNum(curCC.lead_unico, 0);
  document.getElementById('ccOs').innerText = formatNum(curCC.os_geradas, 0);
  document.getElementById('ccPerf').innerText = `${curCC.performance}%`;

  const txBaseEl = document.getElementById('ccTaxaBase');
  if(txBaseEl) txBaseEl.innerText = `${curCC.taxa_os_base ? curCC.taxa_os_base.toFixed(2) : '--'}%`;
  const baseEl = document.getElementById('ccBaseTotal');
  if(baseEl) baseEl.innerText = `Base: ${formatNum(curCC.base_real, 0)} clientes`;

  renderCcMotivosLineChart(curCC);
  renderCcTaxaOsLineChart(curCC);
  renderCcMatrizTable(curCC);
  renderCcSpeechLineChart(curCC);
}

/* =========================================================================
   HISTORICAL LINE CHART: ABERTURAS INVOLUNTÁRIAS (Base, FPD, Opção, Fraude)
   ========================================================================= */
function renderInvolHistoryChart(scope) {
  const container = document.getElementById('involHistoryChart');
  if(!container) return;
  const proj = RAW_DATA.involuntaria_proj;
  if(!proj || !proj.history || proj.history.length === 0) return;

  if(!scope) scope = getActiveScope();
  const isPct = (currentMetric === 'pct');

  let scopeBase = 1;
  if(scope.type === 'CITY') {
    scopeBase = (proj.cities && proj.cities[scope.id] && proj.cities[scope.id].base_real) ||
                (RAW_DATA.cities && RAW_DATA.cities.find(c => c.id === scope.id)?.base_real) ||
                (RAW_DATA.modes['TOTAL'] && RAW_DATA.modes['TOTAL'].cities.find(c => c.id === scope.id)?.base_real) || 1;
  } else if(scope.type === 'GM') {
    scopeBase = (proj.gm && proj.gm.base_real) || (RAW_DATA.subtotals?.gm?.base_real) || (RAW_DATA.modes['TOTAL']?.cities.find(c => c.id === 'GM')?.base_real) || 1;
  } else if(scope.type === 'MD') {
    scopeBase = (proj.md && proj.md.base_real) || (RAW_DATA.subtotals?.md?.base_real) || (RAW_DATA.modes['TOTAL']?.cities.find(c => c.id === 'MD')?.base_real) || 1;
  } else {
    scopeBase = (proj.regional && proj.regional.base_real) || (RAW_DATA.regional?.base_real) || (RAW_DATA.kpis?.base_clientes_real) || 1;
  }

  const rawPts = proj.history;
  const pts = rawPts.map(p => {
    let src = p;
    if(scope.type === 'CITY' && p.cities && p.cities[scope.id]) src = p.cities[scope.id];
    else if(scope.type === 'GM' && p.gm) src = p.gm;
    else if(scope.type === 'MD' && p.md) src = p.md;

    const base = src.base_real || p.base_real || scopeBase || 1;
    if(isPct) {
      return {
        iso: p.iso, label: p.label,
        invol_base: (src.invol_base / base) * 100,
        fpd: (src.fpd / base) * 100,
        opcao: (src.opcao / base) * 100,
        fraude: (src.fraude / base) * 100,
        total: (src.total / base) * 100,
        nominal_total: src.total,
        base_real: base
      };
    }
    return {
      iso: p.iso, label: p.label,
      invol_base: src.invol_base,
      fpd: src.fpd,
      opcao: src.opcao,
      fraude: src.fraude,
      total: src.total,
      nominal_total: src.total,
      base_real: base
    };
  });

  const W = 800, H = 250;
  const padL = isPct ? 55 : 55, padR = 25, padT = 25, padB = 35;
  const plotW = W - padL - padR;
  const plotH = H - padT - padB;

  let maxVal = Math.max(...pts.map(p => Math.max(p.invol_base, p.fpd, p.opcao, p.fraude)));
  if(isPct) {
    maxVal = Math.max(1.5, Math.ceil(maxVal * 10) / 10 * 1.25);
  } else {
    maxVal = Math.max(100, Math.ceil(maxVal / 50) * 50 * 1.15);
  }

  const getX = i => padL + (i / (pts.length - 1)) * plotW;
  const getY = v => padT + (1 - (Math.min(maxVal, Math.max(0, v)) / maxVal)) * plotH;

  const series = [
    { key: 'invol_base', name: 'Involuntária Base', color: '#2a5d8f', width: 2.4 },
    { key: 'fpd', name: 'FPD (1º Pagamento)', color: '#6b4b8a', width: 2.0 },
    { key: 'opcao', name: 'Opção (Involuntária)', color: '#c98a15', width: 1.8 },
    { key: 'fraude', name: 'Fraude SSI', color: '#c0392b', width: 1.8 }
  ];

  let svg = `<svg class="chart-svg" viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg">`;

  // Axis title (Requisito 7)
  svg += `<text x="${padL}" y="13" fill="#8b95a3" font-size="9.5" text-anchor="start">${isPct ? 'Taxa de Churn Involuntário (% da Base)' : 'Volume de Desconexões (Absoluto)'}</text>`;

  const steps = 4;
  for(let i = 0; i <= steps; i++) {
    const val = (maxVal / steps) * i;
    const y = getY(val);
    svg += `<line x1="${padL}" y1="${y}" x2="${padL + plotW}" y2="${y}" stroke="#eceef1" stroke-width="1" />`;
    const labelStr = isPct ? val.toFixed(2) + '%' : formatNum(val, 0);
    svg += `<text x="${padL - 6}" y="${y + 3.5}" fill="#8b95a3" font-size="9.5" text-anchor="end">${labelStr}</text>`;
  }

  series.forEach(s => {
    let lineD = '';
    pts.forEach((p, i) => {
      const val = p[s.key];
      if(val !== undefined && val !== null) {
        lineD += ` ${lineD === '' ? 'M' : 'L'} ${getX(i)} ${getY(val)}`;
      }
    });
    svg += `<path d="${lineD}" fill="none" stroke="${s.color}" stroke-width="${s.width}" opacity="0.9" />`;
  });

  pts.forEach((p, i) => {
    const x = getX(i);
    if(i % 3 === 0 || i === pts.length - 1) {
      svg += `<text x="${x}" y="${padT + plotH + 16}" fill="#8b95a3" font-size="9" text-anchor="middle">${p.label}</text>`;
      svg += `<line x1="${x}" y1="${padT + plotH}" x2="${x}" y2="${padT + plotH + 3}" stroke="#dfe3e8" stroke-width="1" />`;
    }

    series.forEach(s => {
      const val = p[s.key];
      if(val !== undefined && val !== null) {
        const y = getY(val);
        const isLast = (i === pts.length - 1);
        svg += `<circle cx="${x}" cy="${y}" r="${isLast ? 4 : 2.5}" fill="${s.color}" stroke="#fff" stroke-width="1" />`;
      }
    });

    // Unified Month Tooltip (Requisito 3 & 6)
    const monthItems = series.map(s => {
      const val = p[s.key] || 0;
      const valStr = isPct ? `${val.toFixed(2)}%` : formatNum(val, 0);
      const pctOfInvol = p.total > 0 ? ((val / p.total) * 100).toFixed(1) + '%' : '0%';
      return {
        label: s.name,
        val: valStr,
        color: s.color,
        note: `(${pctOfInvol} das invol.)`,
        numVal: val
      };
    }).sort((a, b) => b.numVal - a.numVal);

    const monthTipData = JSON.stringify({
      title: `📅 ${p.label} · Componentes Involuntárias`,
      subtitle: `Escopo: ${scope.label} · ${isPct ? 'Taxa sobre Base' : 'Volume Nominal'}`,
      items: monthItems,
      footer: `Total Involuntárias: ${isPct ? p.total.toFixed(2) + '%' : formatNum(p.total, 0)} (Base: ${formatNum(p.base_real, 0)})`
    }).replace(/"/g, '&quot;');

    const stepW = plotW / (pts.length - 1);
    svg += `<rect x="${x - stepW / 2}" y="${padT}" width="${stepW}" height="${plotH}" fill="transparent"
                 style="cursor:pointer;"
                 onclick="pinTip(event, '${monthTipData}', 'month')"
                 onmouseenter="showMonthTip(event, '${monthTipData}')"
                 onmousemove="positionTip(event)"
                 onmouseleave="hideTip()" />`;
  });

  svg += `</svg>`;
  container.innerHTML = svg;
}

/* =========================================================================
   HISTORICAL LINE CHART: CIDADES NO INVOLUNTÁRIO (Jan/2025 a Set/2026 - Requisito 7)
   ========================================================================= */
function renderInvolCitiesHistoryChart(scope) {
  const container = document.getElementById('involCitiesHistoryChart');
  if(!container) return;
  const proj = RAW_DATA.involuntaria_proj;
  if(!proj || !proj.history || proj.history.length === 0) return;

  if(!scope) scope = getActiveScope();
  const isPct = (currentMetric === 'pct');

  const modeData = RAW_DATA.modes['INVOLUNTARIA'];
  const allCities = modeData.cities.filter(c => c.tipo === 'CIDADE');

  // Palette for 13 cities
  const cityColors = {
    'MANAUS': '#1c4b75', 'BELEM': '#2a5d8f', 'SAO_LUIS': '#457ba8', 'ANANINDEUA': '#5b92bd',
    'MACAPA': '#6b4b8a', 'SANTANA': '#8e6bb0', 'IMPERATRIZ': '#c0392b', 'CASTANHAL': '#d9534f',
    'PARAUAPEBAS': '#c98a15', 'MARABA': '#e0a838', 'PARAGOMINAS': '#27ae60', 'TIMON': '#516173', 'CAXIAS': '#8b95a3'
  };

  const pts = proj.history.map(p => {
    const row = { iso: p.iso, label: p.label };
    allCities.forEach(c => {
      const cData = p.cities ? p.cities[c.id] : null;
      if(cData) {
        if(isPct) {
          const base = cData.base_real || (proj.cities && proj.cities[c.id] && proj.cities[c.id].base_real) || c.base_real || 1;
          row[c.id] = (cData.total / base) * 100;
        } else {
          row[c.id] = cData.total;
        }
      } else {
        row[c.id] = 0;
      }
    });
    return row;
  });

  const W = 800, H = 270;
  const padL = isPct ? 55 : 55, padR = 25, padT = 25, padB = 35;
  const plotW = W - padL - padR;
  const plotH = H - padT - padB;

  let maxVal = 0;
  allCities.forEach(c => {
    pts.forEach(p => {
      if((p[c.id] || 0) > maxVal) maxVal = p[c.id];
    });
  });
  if(isPct) {
    maxVal = Math.max(2.5, Math.ceil(maxVal * 10) / 10 * 1.25);
  } else {
    maxVal = Math.max(100, Math.ceil(maxVal / 50) * 50 * 1.15);
  }

  const getX = i => padL + (i / (pts.length - 1)) * plotW;
  const getY = v => padT + (1 - (Math.min(maxVal, Math.max(0, v)) / maxVal)) * plotH;

  let svg = `<svg class="chart-svg" viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg">`;

  // Axis title
  svg += `<text x="${padL}" y="13" fill="#8b95a3" font-size="9.5" text-anchor="start">${isPct ? 'Taxa de Churn Involuntário por Praça (% da Base)' : 'Volume Nominal de Involuntárias'}</text>`;

  const steps = 4;
  for(let i = 0; i <= steps; i++) {
    const val = (maxVal / steps) * i;
    const y = getY(val);
    svg += `<line x1="${padL}" y1="${y}" x2="${padL + plotW}" y2="${y}" stroke="#eceef1" stroke-width="1" />`;
    const labelStr = isPct ? val.toFixed(2) + '%' : formatNum(val, 0);
    svg += `<text x="${padL - 6}" y="${y + 3.5}" fill="#8b95a3" font-size="9.5" text-anchor="end">${labelStr}</text>`;
  }

  // Render city lines
  allCities.forEach(c => {
    const color = cityColors[c.id] || '#516173';
    let isHighlighted = false;
    let isDimmed = false;

    if(pickedCityId) {
      isHighlighted = (pickedCityId === c.id);
      isDimmed = !isHighlighted;
    } else if(clusterFilter !== 'ALL') {
      isHighlighted = (clusterFilter === c.grupo);
      isDimmed = !isHighlighted;
    }

    const strokeW = isHighlighted ? 3.2 : (isDimmed ? 1.0 : 1.8);
    const strokeOp = isDimmed ? 0.22 : (isHighlighted ? 1.0 : 0.85);

    let lineD = '';
    pts.forEach((p, i) => {
      const val = p[c.id];
      if(val !== undefined && val !== null) {
        lineD += ` ${lineD === '' ? 'M' : 'L'} ${getX(i)} ${getY(val)}`;
      }
    });
    svg += `<path d="${lineD}" fill="none" stroke="${color}" stroke-width="${strokeW}" opacity="${strokeOp}" />`;
  });

  // Month axes and tooltips
  pts.forEach((p, i) => {
    const x = getX(i);
    if(i % 3 === 0 || i === pts.length - 1) {
      svg += `<text x="${x}" y="${padT + plotH + 16}" fill="#8b95a3" font-size="9" text-anchor="middle">${p.label}</text>`;
      svg += `<line x1="${x}" y1="${padT + plotH}" x2="${x}" y2="${padT + plotH + 3}" stroke="#dfe3e8" stroke-width="1" />`;
    }

    // Dots for highlighted or all
    allCities.forEach(c => {
      if(pickedCityId && pickedCityId !== c.id) return;
      if(!pickedCityId && clusterFilter !== 'ALL' && clusterFilter !== c.grupo) return;

      const val = p[c.id];
      if(val !== undefined && val !== null) {
        const y = getY(val);
        const isLast = (i === pts.length - 1);
        const color = cityColors[c.id] || '#516173';
        svg += `<circle cx="${x}" cy="${y}" r="${isLast ? 4 : 2.5}" fill="${color}" stroke="#fff" stroke-width="1" />`;
      }
    });

    // Unified Month Tooltip (Requisito 3 & 6)
    const monthItems = allCities.map(c => {
      const val = p[c.id] || 0;
      return {
        label: `${c.nome} (${c.uf})`,
        val: isPct ? `${val.toFixed(2)}%` : formatNum(val, 0),
        color: cityColors[c.id] || '#516173',
        numVal: val
      };
    }).sort((a, b) => b.numVal - a.numVal);

    const monthTipData = JSON.stringify({
      title: `📅 ${p.label} · Desconexões Involuntárias por Cidade`,
      subtitle: `${isPct ? 'Taxa de Involuntárias sobre a Base' : 'Volume Nominal de Involuntárias'}`,
      items: monthItems,
      footer: `Clique numa praça na tabela para focar a análise`
    }).replace(/"/g, '&quot;');

    const stepW = plotW / (pts.length - 1);
    svg += `<rect x="${x - stepW / 2}" y="${padT}" width="${stepW}" height="${plotH}" fill="transparent"
                 style="cursor:pointer;"
                 onclick="pinTip(event, '${monthTipData}', 'month')"
                 onmouseenter="showMonthTip(event, '${monthTipData}')"
                 onmousemove="positionTip(event)"
                 onmouseleave="hideTip()" />`;
  });

  svg += `</svg>`;
  container.innerHTML = svg;

  // Render Legend
  const legendEl = document.getElementById('involCitiesLegend');
  if(legendEl) {
    let lHtml = '';
    allCities.forEach(c => {
      const color = cityColors[c.id] || '#516173';
      const isPicked = (pickedCityId === c.id);
      const style = isPicked ? 'font-weight:700; color:var(--ink);' : '';
      lHtml += `<span style="cursor:pointer; ${style}" onclick="selectCity('${c.id}')"><i style="background:${color}; border-radius:50%;"></i>${c.nome}</span>`;
    });
    legendEl.innerHTML = lHtml;
  }
}

/* =========================================================================
   ACESSÓRIO: MODELO PROJEÇÃO (Desconexão Involuntária)
   ========================================================================= */
function renderInvoluntariaModule() {
  const proj = RAW_DATA.involuntaria_proj;
  if(!proj) return;
  const scope = getActiveScope();
  const isPct = (currentMetric === 'pct');

  const scopeBadge = document.getElementById('involScopeBadge');
  if(scopeBadge) {
    scopeBadge.className = `tag ${scope.badgeClass}`;
    scopeBadge.innerText = scope.label;
  }

  let curProj = proj.regional;
  if(scope.type === 'CITY' && proj.cities && proj.cities[scope.id]) curProj = proj.cities[scope.id];
  else if(scope.type === 'GM' && proj.gm) curProj = proj.gm;
  else if(scope.type === 'MD' && proj.md) curProj = proj.md;

  if(isPct) {
    document.getElementById('involBase').innerText = `${curProj.taxa_base ? curProj.taxa_base.toFixed(2) : '--'}%`;
    document.getElementById('involBasePct').innerText = `${curProj.pct_base}% das invol. | Volume: ${formatNum(curProj.invol_base, 0)}`;

    document.getElementById('involFpd').innerText = `${curProj.taxa_fpd ? curProj.taxa_fpd.toFixed(2) : '--'}%`;
    document.getElementById('involFpdPct').innerText = `${curProj.pct_fpd}% das invol. | Volume: ${formatNum(curProj.fpd, 0)}`;

    document.getElementById('involOpcao').innerText = `${curProj.taxa_opcao ? curProj.taxa_opcao.toFixed(2) : '--'}%`;
    document.getElementById('involOpcaoPct').innerText = `${curProj.pct_opcao}% das invol. | Volume: ${formatNum(curProj.opcao, 0)}`;

    document.getElementById('involFraude').innerText = `${curProj.taxa_fraude ? curProj.taxa_fraude.toFixed(2) : '--'}%`;
    document.getElementById('involFraudePct').innerText = `${curProj.pct_fraude}% das invol. | Volume: ${formatNum(curProj.fraude, 0)}`;
  } else {
    document.getElementById('involBase').innerText = formatNum(curProj.invol_base, 0);
    document.getElementById('involBasePct').innerText = `${curProj.pct_base}% das invol. | Taxa: ${curProj.taxa_base ? curProj.taxa_base.toFixed(2) : '--'}% da base`;

    document.getElementById('involFpd').innerText = formatNum(curProj.fpd, 0);
    document.getElementById('involFpdPct').innerText = `${curProj.pct_fpd}% das invol. | Taxa: ${curProj.taxa_fpd ? curProj.taxa_fpd.toFixed(2) : '--'}% da base`;

    document.getElementById('involOpcao').innerText = formatNum(curProj.opcao, 0);
    document.getElementById('involOpcaoPct').innerText = `${curProj.pct_opcao}% das invol. | Taxa: ${curProj.taxa_opcao ? curProj.taxa_opcao.toFixed(2) : '--'}% da base`;

    document.getElementById('involFraude').innerText = formatNum(curProj.fraude, 0);
    document.getElementById('involFraudePct').innerText = `${curProj.pct_fraude}% das invol. | Taxa: ${curProj.taxa_fraude ? curProj.taxa_fraude.toFixed(2) : '--'}% da base`;
  }

  renderInvolHistoryChart(scope);
  renderInvolCitiesHistoryChart(scope);

  // Tabela Completa por praça com 4 pilares, participações, taxas de churn, MoM e YoY
  const tbody = document.getElementById('tblInvolProjBody');
  if(!tbody) return;
  let html = '';
  
  const modeData = RAW_DATA.modes['INVOLUNTARIA'];
  const cities = modeData.cities.filter(c => c.tipo === 'CIDADE');
  const gmList = cities.filter(c => c.grupo === 'GM');
  const mdList = cities.filter(c => c.grupo === 'MD');

  const fmtSign = (v) => {
    if(v === null || v === undefined || isNaN(v)) return '--';
    const color = v < 0 ? 'color:var(--green); font-weight:600;' : (v > 0 ? 'color:var(--red); font-weight:600;' : 'color:var(--ink3);');
    return `<span style="${color}">${v > 0 ? '+' : ''}${v.toFixed(1)}%</span>`;
  };

  const renderProjRow = (c) => {
    const p = proj.cities[c.id] || {
      invol_base: 0, fpd: 0, opcao: 0, fraude: 0, total: 0, base_real: c.base_real || 0,
      pct_base: 0, pct_fpd: 0, pct_opcao: 0, pct_fraude: 0,
      taxa_base: 0, taxa_fpd: 0, taxa_opcao: 0, taxa_fraude: 0, taxa_total: 0,
      mom_base_pct: 0, mom_fpd_pct: 0, mom_opcao_pct: 0, mom_fraude_pct: 0, mom_total_pct: 0,
      yoy_base_pct: 0, yoy_fpd_pct: 0, yoy_opcao_pct: 0, yoy_fraude_pct: 0, yoy_total_pct: 0
    };
    const isPicked = (pickedCityId === c.id);
    const rowBg = isPicked ? 'background:#edf3f9; border-left:3px solid var(--blue);' : '';

    return `<tr style="cursor:pointer; ${rowBg}" onclick="selectCity('${c.id}')">
      <td class="l" style="font-weight:700; color:var(--blue);">${c.nome}</td>
      <td class="l">${c.grupo === 'GM' ? '<span class="cluster-badge gm">GM</span>' : '<span class="cluster-badge md">MD</span>'}</td>
      <td>${formatNum(p.base_real, 0)}</td>
      <td class="col-sep">${formatNum(p.invol_base, 0)}</td>
      <td>${formatNum(p.fpd, 0)}</td>
      <td>${formatNum(p.opcao, 0)}</td>
      <td>${formatNum(p.fraude, 0)}</td>
      <td style="font-weight:700;">${formatNum(p.total, 0)}</td>
      <td class="col-sep" style="color:var(--blue); font-weight:600;">${p.pct_base}%</td>
      <td style="color:var(--purple); font-weight:600;">${p.pct_fpd}%</td>
      <td style="color:var(--amber); font-weight:600;">${p.pct_opcao}%</td>
      <td style="color:var(--red); font-weight:600;">${p.pct_fraude}%</td>
      <td class="col-sep" style="font-weight:600;">${p.taxa_base ? p.taxa_base.toFixed(2) : '--'}%</td>
      <td style="font-weight:600;">${p.taxa_fpd ? p.taxa_fpd.toFixed(2) : '--'}%</td>
      <td style="font-weight:600;">${p.taxa_opcao ? p.taxa_opcao.toFixed(2) : '--'}%</td>
      <td style="font-weight:600;">${p.taxa_fraude ? p.taxa_fraude.toFixed(2) : '--'}%</td>
      <td style="font-weight:800; color:var(--red);">${p.taxa_total ? p.taxa_total.toFixed(2) : '--'}%</td>
      <td class="col-sep">${fmtSign(p.mom_base_pct)}</td>
      <td>${fmtSign(p.mom_fpd_pct)}</td>
      <td>${fmtSign(p.mom_opcao_pct)}</td>
      <td>${fmtSign(p.mom_fraude_pct)}</td>
      <td style="font-weight:700;">${fmtSign(p.mom_total_pct)}</td>
      <td class="col-sep">${fmtSign(p.yoy_base_pct)}</td>
      <td>${fmtSign(p.yoy_fpd_pct)}</td>
      <td>${fmtSign(p.yoy_opcao_pct)}</td>
      <td>${fmtSign(p.yoy_fraude_pct)}</td>
      <td style="font-weight:700;">${fmtSign(p.yoy_total_pct)}</td>
    </tr>`;
  };

  const renderGroupHeader = (name, badge, p) => {
    return `<tr class="section-divider-row" style="background:#f4f6f9; font-weight:700; border-top:2px solid #b2c1d3; border-bottom:1px solid #b2c1d3;">
      <td class="l" style="font-weight:700;"><span class="cluster-badge ${badge}">${name}</span></td>
      <td class="l"><span class="cluster-badge ${badge}">${badge.toUpperCase()}</span></td>
      <td>${formatNum(p.base_real, 0)}</td>
      <td class="col-sep">${formatNum(p.invol_base, 0)}</td>
      <td>${formatNum(p.fpd, 0)}</td>
      <td>${formatNum(p.opcao, 0)}</td>
      <td>${formatNum(p.fraude, 0)}</td>
      <td style="font-weight:800;">${formatNum(p.total, 0)}</td>
      <td class="col-sep" style="color:var(--blue); font-weight:600;">${p.pct_base}%</td>
      <td style="color:var(--purple); font-weight:600;">${p.pct_fpd}%</td>
      <td style="color:var(--amber); font-weight:600;">${p.pct_opcao}%</td>
      <td style="color:var(--red); font-weight:600;">${p.pct_fraude}%</td>
      <td class="col-sep" style="font-weight:600;">${p.taxa_base ? p.taxa_base.toFixed(2) : '--'}%</td>
      <td style="font-weight:600;">${p.taxa_fpd ? p.taxa_fpd.toFixed(2) : '--'}%</td>
      <td style="font-weight:600;">${p.taxa_opcao ? p.taxa_opcao.toFixed(2) : '--'}%</td>
      <td style="font-weight:600;">${p.taxa_fraude ? p.taxa_fraude.toFixed(2) : '--'}%</td>
      <td style="font-weight:800; color:var(--red);">${p.taxa_total ? p.taxa_total.toFixed(2) : '--'}%</td>
      <td class="col-sep">${fmtSign(p.mom_base_pct)}</td>
      <td>${fmtSign(p.mom_fpd_pct)}</td>
      <td>${fmtSign(p.mom_opcao_pct)}</td>
      <td>${fmtSign(p.mom_fraude_pct)}</td>
      <td style="font-weight:700;">${fmtSign(p.mom_total_pct)}</td>
      <td class="col-sep">${fmtSign(p.yoy_base_pct)}</td>
      <td>${fmtSign(p.yoy_fpd_pct)}</td>
      <td>${fmtSign(p.yoy_opcao_pct)}</td>
      <td>${fmtSign(p.yoy_fraude_pct)}</td>
      <td style="font-weight:700;">${fmtSign(p.yoy_total_pct)}</td>
    </tr>`;
  };

  const renderGroupSubtotal = (name, badge, p) => {
    return `<tr style="background:#eef2f6; font-weight:700; border-top:1px solid #dfe3e8; border-bottom:1px solid #dfe3e8;">
      <td class="l">${name}</td>
      <td class="l"><span class="cluster-badge ${badge}">${badge.toUpperCase()}</span></td>
      <td>${formatNum(p.base_real, 0)}</td>
      <td class="col-sep">${formatNum(p.invol_base, 0)}</td>
      <td>${formatNum(p.fpd, 0)}</td>
      <td>${formatNum(p.opcao, 0)}</td>
      <td>${formatNum(p.fraude, 0)}</td>
      <td style="font-weight:800;">${formatNum(p.total, 0)}</td>
      <td class="col-sep">${p.pct_base}%</td>
      <td>${p.pct_fpd}%</td>
      <td>${p.pct_opcao}%</td>
      <td>${p.pct_fraude}%</td>
      <td class="col-sep">${p.taxa_base ? p.taxa_base.toFixed(2) : '--'}%</td>
      <td>${p.taxa_fpd ? p.taxa_fpd.toFixed(2) : '--'}%</td>
      <td>${p.taxa_opcao ? p.taxa_opcao.toFixed(2) : '--'}%</td>
      <td>${p.taxa_fraude ? p.taxa_fraude.toFixed(2) : '--'}%</td>
      <td style="font-weight:800; color:var(--red);">${p.taxa_total ? p.taxa_total.toFixed(2) : '--'}%</td>
      <td class="col-sep">${fmtSign(p.mom_base_pct)}</td>
      <td>${fmtSign(p.mom_fpd_pct)}</td>
      <td>${fmtSign(p.mom_opcao_pct)}</td>
      <td>${fmtSign(p.mom_fraude_pct)}</td>
      <td>${fmtSign(p.mom_total_pct)}</td>
      <td class="col-sep">${fmtSign(p.yoy_base_pct)}</td>
      <td>${fmtSign(p.yoy_fpd_pct)}</td>
      <td>${fmtSign(p.yoy_opcao_pct)}</td>
      <td>${fmtSign(p.yoy_fraude_pct)}</td>
      <td>${fmtSign(p.yoy_total_pct)}</td>
    </tr>`;
  };

  if(clusterFilter === 'ALL' || clusterFilter === 'GM') {
    html += renderGroupHeader('Grandes Mercados (GM)', 'gm', proj.gm);
    gmList.forEach(c => html += renderProjRow(c));
    html += renderGroupSubtotal('SUBTOTAL GRANDES MERCADOS', 'gm', proj.gm);
  }

  if(clusterFilter === 'ALL' || clusterFilter === 'MD') {
    html += renderGroupHeader('Mercados em Desenvolvimento (MD)', 'md', proj.md);
    mdList.forEach(c => html += renderProjRow(c));
    html += renderGroupSubtotal('SUBTOTAL MERCADOS EM DESENV.', 'md', proj.md);
  }

  const reg = proj.regional;
  html += `<tr style="background:#e8edf3; font-weight:800; border-top:2px solid var(--nav); font-size:12px;">
    <td class="l">TOTAL REGIONAL NORTE</td>
    <td class="l">REGIONAL</td>
    <td>${formatNum(reg.base_real, 0)}</td>
    <td class="col-sep">${formatNum(reg.invol_base, 0)}</td>
    <td>${formatNum(reg.fpd, 0)}</td>
    <td>${formatNum(reg.opcao, 0)}</td>
    <td>${formatNum(reg.fraude, 0)}</td>
    <td style="color:var(--red); font-size:13px;">${formatNum(reg.total, 0)}</td>
    <td class="col-sep" style="color:var(--blue);">${reg.pct_base}%</td>
    <td style="color:var(--purple);">${reg.pct_fpd}%</td>
    <td style="color:var(--amber);">${reg.pct_opcao}%</td>
    <td style="color:var(--red);">${reg.pct_fraude}%</td>
    <td class="col-sep">${reg.taxa_base ? reg.taxa_base.toFixed(2) : '--'}%</td>
    <td>${reg.taxa_fpd ? reg.taxa_fpd.toFixed(2) : '--'}%</td>
    <td>${reg.taxa_opcao ? reg.taxa_opcao.toFixed(2) : '--'}%</td>
    <td>${reg.taxa_fraude ? reg.taxa_fraude.toFixed(2) : '--'}%</td>
    <td style="color:var(--red); font-size:13px;">${reg.taxa_total ? reg.taxa_total.toFixed(2) : '--'}%</td>
    <td class="col-sep">${fmtSign(reg.mom_base_pct)}</td>
    <td>${fmtSign(reg.mom_fpd_pct)}</td>
    <td>${fmtSign(reg.mom_opcao_pct)}</td>
    <td>${fmtSign(reg.mom_fraude_pct)}</td>
    <td>${fmtSign(reg.mom_total_pct)}</td>
    <td class="col-sep">${fmtSign(reg.yoy_base_pct)}</td>
    <td>${fmtSign(reg.yoy_fpd_pct)}</td>
    <td>${fmtSign(reg.yoy_opcao_pct)}</td>
    <td>${fmtSign(reg.yoy_fraude_pct)}</td>
    <td>${fmtSign(reg.yoy_total_pct)}</td>
  </tr>`;

  tbody.innerHTML = html;
}

/* =========================================================================
   SCATTER BUBBLE CHART (MoM vs YoY) - Requisito 2 & 8
   ========================================================================= */
function renderScatterChart() {
  const container = document.getElementById('scatterContainer');
  if(!container) return;
  const modeData = RAW_DATA.modes[currentMode];
  let cities = modeData.cities.filter(c => c.tipo === 'CIDADE');

  if(clusterFilter !== 'ALL') {
    cities = cities.filter(c => c.grupo === clusterFilter);
  }

  // Requisito 2: Quando selecionar uma cidade, o gráfico de dispersão deve mostrar apenas essa cidade
  if(pickedCityId) {
    cities = cities.filter(c => c.id === pickedCityId);
  }

  const scope = getActiveScope();
  const isPct = (currentMetric === 'pct');

  const sTag = document.getElementById('scatterScopeTag');
  if(sTag) {
    sTag.style.display = 'inline-block';
    sTag.className = `tag ${scope.badgeClass}`;
    sTag.innerText = scope.label;
  }

  const noteEl = document.getElementById('scatterNote');
  if(noteEl) {
    noteEl.innerText = isPct
      ? 'Tamanho da bolha = Taxa de Churn (%) · Clique na praça para isolar'
      : 'Tamanho da bolha = Volume de Desconexões · Clique na praça para isolar';
  }

  const W = 800;
  const H = 380;
  const padL = 60, padR = 40, padT = 30, padB = 40;
  const plotW = W - padL - padR;
  const plotH = H - padT - padB;

  let momVals = cities.map(c => c.mom_pct || 0);
  let yoyVals = cities.map(c => c.yoy_pct || 0);
  let sizeVals = cities.map(c => (isPct ? (c.taxa_real || 0.1) : (c.vol_real || 1)));

  let maxMoMAbs = Math.max(25, ...momVals.map(v => Math.abs(v)));
  maxMoMAbs = Math.ceil(maxMoMAbs / 5) * 5 + 5;
  const minX = -maxMoMAbs;
  const maxX = maxMoMAbs;

  let minY = Math.min(-30, ...yoyVals);
  let maxY = Math.max(30, ...yoyVals);
  minY = Math.floor(minY / 10) * 10 - 5;
  maxY = Math.ceil(maxY / 10) * 10 + 5;

  const maxSize = Math.max(...sizeVals);
  const minSize = Math.min(...sizeVals);

  const scaleX = v => padL + ((v - minX) / (maxX - minX)) * plotW;
  const scaleY = v => padT + ((maxY - v) / (maxY - minY)) * plotH;
  const scaleR = v => {
    if(cities.length === 1) return 18;
    const minR = 7, maxR = 26;
    if(maxSize === minSize) return 14;
    return minR + Math.sqrt(Math.max(0, v) / maxSize) * (maxR - minR);
  };

  const zeroX = scaleX(0);
  const zeroY = scaleY(0);

  let svg = `<svg class="chart-svg" viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg">`;

  svg += `<rect x="${zeroX}" y="${padT}" width="${padL + plotW - zeroX}" height="${zeroY - padT}" fill="#fdece9" opacity="0.45" />`;
  svg += `<rect x="${padL}" y="${zeroY}" width="${zeroX - padL}" height="${padT + plotH - zeroY}" fill="#eaf2ec" opacity="0.45" />`;
  svg += `<rect x="${padL}" y="${padT}" width="${zeroX - padL}" height="${zeroY - padT}" fill="#fdf3e2" opacity="0.3" />`;
  svg += `<rect x="${zeroX}" y="${zeroY}" width="${padL + plotW - zeroX}" height="${padT + plotH - zeroY}" fill="#fdf3e2" opacity="0.3" />`;

  [-30, -20, -10, 10, 20, 30].forEach(val => {
    if(val > minX && val < maxX) {
      const x = scaleX(val);
      svg += `<line x1="${x}" y1="${padT}" x2="${x}" y2="${padT + plotH}" stroke="#eceef1" stroke-width="1" />`;
      svg += `<text x="${x}" y="${padT + plotH + 16}" fill="#8b95a3" font-size="10" text-anchor="middle">${val}%</text>`;
    }
  });

  svg += `<line x1="${padL}" y1="${zeroY}" x2="${padL + plotW}" y2="${zeroY}" stroke="#5b6675" stroke-width="1.4" stroke-dasharray="3,3" />`;
  svg += `<line x1="${zeroX}" y1="${padT}" x2="${zeroX}" y2="${padT + plotH}" stroke="#5b6675" stroke-width="1.4" stroke-dasharray="3,3" />`;

  svg += `<text x="${zeroX + 4}" y="${padT + 12}" fill="#5b6675" font-size="10" font-weight="600">YoY = 0%</text>`;
  svg += `<text x="${padL + plotW - 4}" y="${zeroY - 6}" fill="#5b6675" font-size="10" font-weight="600" text-anchor="end">MoM = 0%</text>`;
  svg += `<text x="${W / 2}" y="${H - 6}" fill="#1c2430" font-size="11" font-weight="600" text-anchor="middle">Variação Mensal MoM (%) →</text>`;
  svg += `<text x="14" y="${H / 2}" fill="#1c2430" font-size="11" font-weight="600" text-anchor="middle" transform="rotate(-90 14 ${H/2})">↑ Variação Anual YoY (%)</text>`;

  svg += `<text x="${padL + plotW - 8}" y="${padT + 16}" fill="#9b1c1c" font-size="10.5" font-weight="700" text-anchor="end">OFENSORES CRÍTICOS (MoM+ / YoY+)</text>`;
  svg += `<text x="${padL + 8}" y="${padT + plotH - 8}" fill="#235c44" font-size="10.5" font-weight="700">MELHORA GERAL (MoM- / YoY-)</text>`;
  svg += `<text x="${padL + 8}" y="${padT + 16}" fill="#8a5d06" font-size="10" font-weight="600">RECUPERAÇÃO RECENTE (MoM- / YoY+)</text>`;
  svg += `<text x="${padL + plotW - 8}" y="${padT + plotH - 8}" fill="#8a5d06" font-size="10" font-weight="600" text-anchor="end">ALERTA INFLEXÃO (MoM+ / YoY-)</text>`;

  cities.forEach(c => {
    const cx = scaleX(c.mom_pct || 0);
    const cy = scaleY(c.yoy_pct || 0);
    const sizeVal = isPct ? (c.taxa_real || 0.1) : (c.vol_real || 0);
    const r = scaleR(sizeVal);
    const isGM = c.grupo === 'GM';
    const color = isGM ? '#2a5d8f' : '#c98a15';
    const strokeColor = isGM ? '#173656' : '#805304';
    const isPicked = (pickedCityId === c.id);

    const taxaAgo = (c.vol_ago26 && c.base_real) ? (c.vol_ago26 / c.base_real) * 100 : null;
    const momPp = (c.taxa_real !== null && taxaAgo !== null) ? (c.taxa_real - taxaAgo) : null;
    const taxaSep25 = (c.vol_sep25 && c.base_real) ? (c.vol_sep25 / c.base_real) * 100 : null;
    const yoyPp = (c.taxa_real !== null && taxaSep25 !== null) ? (c.taxa_real - taxaSep25) : null;

    const tooltipData = JSON.stringify({
      nome: c.nome,
      uf: c.uf,
      grupo: isGM ? 'Grandes Mercados' : 'Mercados em Desenvolvimento',
      vol: c.vol_real,
      orc: c.vol_orc,
      rxo_delta: c.rxo_delta,
      rxo_pct: c.rxo_pct,
      mom_pct: c.mom_pct,
      mom_delta: c.mom_delta,
      vol_sep25: c.vol_sep25,
      yoy_pct: c.yoy_pct,
      yoy_delta: c.yoy_delta,
      taxa: c.taxa_real,
      taxa_orc: c.taxa_orc,
      taxa_delta_pp: c.taxa_delta_pp,
      mom_pp: momPp,
      yoy_pp: yoyPp,
      base: c.base_real
    }).replace(/"/g, '&quot;');

    svg += `<g class="scatter-bubble" style="cursor:pointer;" onclick="selectCity('${c.id}'); pinTip(event, '${tooltipData}', 'bubble');"
               onmouseenter="showBubbleTip(event, '${tooltipData}')" onmousemove="positionTip(event)" onmouseleave="hideTip()">`;
    svg += `<circle cx="${cx}" cy="${cy}" r="${r}" fill="${color}" fill-opacity="${isPicked ? '0.95' : '0.7'}"
                   stroke="${strokeColor}" stroke-width="${isPicked ? '3' : '1.4'}" />`;
    svg += `<text x="${cx}" y="${cy - r - 4}" fill="#1c2430" font-size="${r > 16 ? '11' : '10'}" font-weight="${r > 16 ? '700' : '600'}" text-anchor="middle">${c.nome}</text>`;
    svg += `</g>`;
  });

  svg += `</svg>`;
  container.innerHTML = svg;
}

/* =========================================================================
   TIMELINE CHART (33 Meses: Jan/2024 a Set/2026) - Requisito 8
   ========================================================================= */
function renderTimelineChart() {
  const container = document.getElementById('timelineContainer');
  const modeData = RAW_DATA.modes[currentMode];
  const pts = modeData.timeline;
  if(!pts || pts.length === 0) return;

  const scope = getActiveScope();
  const isPct = (currentMetric === 'pct');

  const tTag = document.getElementById('timelineScopeTag');
  if(tTag) {
    tTag.style.display = 'inline-block';
    tTag.className = `tag ${scope.badgeClass}`;
    tTag.innerText = scope.label;
  }

  const tNote = document.getElementById('timelineNote');
  if(tNote) {
    tNote.innerText = isPct
      ? '33 meses · Comparativo Taxa Realizada (%) vs Orçamento (%)'
      : '33 meses · Comparativo Realizado vs Orçamento';
  }

  const W = 800;
  const H = 380;
  const padL = 55, padR = 25, padT = 30, padB = 40;
  const plotW = W - padL - padR;
  const plotH = H - padT - padB;

  let baseReal = 1, baseOrc = 1;
  const baseGM = modeData.cities.find(c => c.id === 'GM')?.base_real || 385622;
  const baseMD = modeData.cities.find(c => c.id === 'MD')?.base_real || 34481;
  if(pickedCityId) {
    const c = modeData.cities.find(x => x.id === pickedCityId);
    baseReal = c?.base_real || 1;
    baseOrc = c?.base_orc || baseReal;
  } else if(clusterFilter === 'GM') {
    baseReal = baseGM;
    baseOrc = modeData.cities.find(c => c.id === 'GM')?.base_orc || baseReal;
  } else if(clusterFilter === 'MD') {
    baseReal = baseMD;
    baseOrc = modeData.cities.find(c => c.id === 'MD')?.base_orc || baseReal;
  } else {
    baseReal = modeData.cities.find(c => c.tipo === 'TOTAL')?.base_real || 420835;
    baseOrc = modeData.cities.find(c => c.tipo === 'TOTAL')?.base_orc || baseReal;
  }

  // Determine active series values
  const getPReal = p => {
    let raw = null;
    if(pickedCityId && p.cities && p.cities[pickedCityId]) {
      raw = p.cities[pickedCityId].realizado;
    } else {
      raw = (clusterFilter === 'GM' ? p.gm_real : (clusterFilter === 'MD' ? p.md_real : p.realizado));
    }
    if(raw === null || raw === undefined) return null;
    return isPct ? (raw / baseReal) * 100 : raw;
  };

  const getPOrc = p => {
    let raw = null;
    if(pickedCityId && p.cities && p.cities[pickedCityId]) {
      raw = p.cities[pickedCityId].orcamento;
    } else {
      raw = (clusterFilter === 'GM' ? p.gm_orc : (clusterFilter === 'MD' ? p.md_orc : p.orcamento));
    }
    if(raw === null || raw === undefined) return null;
    return isPct ? (raw / baseOrc) * 100 : raw;
  };

  let maxVal = Math.max(...pts.map(p => Math.max(getPReal(p) || 0, getPOrc(p) || 0)));
  if(isPct) {
    maxVal = Math.max(3, Math.ceil(maxVal * 10) / 10 * 1.25);
  } else {
    maxVal = Math.max(100, Math.ceil(maxVal / 500) * 500 * 1.1);
  }

  const getX = i => padL + (i / (pts.length - 1)) * plotW;
  const getY = v => padT + (1 - (v / maxVal)) * plotH;

  let svg = `<svg class="chart-svg" viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg">`;

  // Axis title
  svg += `<text x="${padL}" y="14" fill="#8b95a3" font-size="9.5" text-anchor="start">${isPct ? 'Taxa de Churn (% da Base)' : 'Volume de Desconexões (Absoluto)'}</text>`;

  const steps = 5;
  for(let i = 0; i <= steps; i++) {
    const val = (maxVal / steps) * i;
    const y = getY(val);
    svg += `<line x1="${padL}" y1="${y}" x2="${padL + plotW}" y2="${y}" stroke="#eceef1" stroke-width="1" />`;
    const labelStr = isPct ? val.toFixed(2) + '%' : formatNum(val, 0);
    svg += `<text x="${padL - 8}" y="${y + 3.5}" fill="#8b95a3" font-size="10" text-anchor="end">${labelStr}</text>`;
  }

  // Area under active series
  let areaD = `M ${getX(0)} ${padT + plotH}`;
  pts.forEach((p, i) => {
    const v = getPReal(p);
    if(v !== null && v !== undefined) areaD += ` L ${getX(i)} ${getY(v)}`;
  });
  areaD += ` L ${getX(pts.length - 1)} ${padT + plotH} Z`;
  svg += `<path d="${areaD}" fill="#c0392b" fill-opacity="0.08" />`;

  // Active budget line (dashed blue)
  let lineOrc = '';
  pts.forEach((p, i) => {
    const v = getPOrc(p);
    if(v !== null && v !== undefined) {
      const cmd = lineOrc === '' ? 'M' : 'L';
      lineOrc += ` ${cmd} ${getX(i)} ${getY(v)}`;
    }
  });
  svg += `<path d="${lineOrc}" fill="none" stroke="#2a5d8f" stroke-width="2.2" stroke-dasharray="5,4" />`;

  // Secondary reference lines (only if ALL and no picked city)
  if(!pickedCityId && clusterFilter === 'ALL') {
    let lineGM = '', lineMD = '';
    pts.forEach((p, i) => {
      const gmV = isPct ? (p.gm_real / baseGM) * 100 : p.gm_real;
      const mdV = isPct ? (p.md_real / baseMD) * 100 : p.md_real;
      if(gmV !== null && !isNaN(gmV)) lineGM += ` ${lineGM === '' ? 'M' : 'L'} ${getX(i)} ${getY(gmV)}`;
      if(mdV !== null && !isNaN(mdV)) lineMD += ` ${lineMD === '' ? 'M' : 'L'} ${getX(i)} ${getY(mdV)}`;
    });
    svg += `<path d="${lineGM}" fill="none" stroke="#516173" stroke-width="1.4" opacity="0.8" />`;
    svg += `<path d="${lineMD}" fill="none" stroke="#c98a15" stroke-width="1.4" opacity="0.85" />`;
  }

  // Active Real line (bold red)
  let lineReal = '';
  pts.forEach((p, i) => {
    const v = getPReal(p);
    if(v !== null && v !== undefined) {
      lineReal += ` ${lineReal === '' ? 'M' : 'L'} ${getX(i)} ${getY(v)}`;
    }
  });
  svg += `<path d="${lineReal}" fill="none" stroke="#c0392b" stroke-width="2.6" />`;

  pts.forEach((p, i) => {
    const x = getX(i);
    if(i % 3 === 0 || i === pts.length - 1) {
      svg += `<text x="${x}" y="${padT + plotH + 16}" fill="#8b95a3" font-size="9.5" text-anchor="middle">${p.label}</text>`;
      svg += `<line x1="${x}" y1="${padT + plotH}" x2="${x}" y2="${padT + plotH + 4}" stroke="#dfe3e8" stroke-width="1" />`;
    }

    const realV = getPReal(p);
    const orcV = getPOrc(p);
    if(realV !== null && realV !== undefined) {
      const y = getY(realV);
      const isLast = (i === pts.length - 1);
      const gmV = isPct ? (p.gm_real / baseGM) * 100 : p.gm_real;
      const mdV = isPct ? (p.md_real / baseMD) * 100 : p.md_real;

      const tipData = JSON.stringify({
        mes: p.label,
        iso: p.iso,
        realizado: realV,
        orcamento: orcV,
        gm_real: gmV,
        md_real: mdV,
        isPct: isPct,
        escopo: scope.label
      }).replace(/"/g, '&quot;');

      svg += `<circle cx="${x}" cy="${y}" r="${isLast ? 4.8 : 3.2}" fill="#c0392b" stroke="#fff" stroke-width="1.5" />`;

      const stepW = plotW / (pts.length - 1);
      svg += `<rect x="${x - stepW / 2}" y="${padT}" width="${stepW}" height="${plotH}" fill="transparent"
                   style="cursor:pointer;"
                   onclick="pinTip(event, '${tipData}', 'timeline')"
                   onmouseenter="showTimelineTip(event, '${tipData}')"
                   onmousemove="positionTip(event)"
                   onmouseleave="hideTip()" />`;
    }
  });

  svg += `</svg>`;
  container.innerHTML = svg;
}

/* =========================================================================
   TABLE RENDERING: RIGOROUS SEPARATION OF GM AND MD + YOY & YTD 26x25
   ========================================================================= */
function renderTable() {
  const tbody = document.getElementById('tblBody');
  const tfoot = document.getElementById('tblFoot');
  const modeData = RAW_DATA.modes[currentMode];
  let allCities = [...modeData.cities];

  const isPct = (currentMetric === 'pct');

  // Update table header labels based on metric mode (Requisito 8)
  const setHText = (id, text) => {
    const el = document.getElementById(id);
    if(el) el.innerText = text;
  };
  setHText('thVolReal', isPct ? 'Taxa Real' : 'Real (T4)');
  setHText('thVolOrc', isPct ? 'Taxa Orç' : 'Orçado');
  setHText('thRxoDelta', isPct ? 'Δ RxO (p.p.)' : 'Δ RxO');
  setHText('thRxoVar', isPct ? 'Var (p.p.)' : 'Var %');
  setHText('thMomVar', isPct ? 'MoM (p.p.)' : 'MoM %');
  setHText('thVolSep25', isPct ? 'Taxa Set/25' : 'Set/25');
  setHText('thYoyVar', isPct ? 'YoY (p.p.)' : 'YoY %');
  setHText('thYtdReal', isPct ? 'YTD Real (%)' : 'YTD 2026');
  setHText('thYtd2025', isPct ? 'YTD 2025 (%)' : 'YTD 2025');
  setHText('thYtdDelta', isPct ? 'Δ 26x25 (p.p.)' : 'Δ 26x25');
  setHText('thYtdVar', isPct ? 'Var (p.p.)' : 'Var %');
  setHText('thYtdOrc', isPct ? 'YTD Orç (%)' : 'YTD Orç');
  setHText('thYtdRxo', isPct ? 'RxO YTD (p.p.)' : 'RxO YTD %');
  setHText('thT1', isPct ? 'T1 (%)' : 'T1');
  setHText('thT2', isPct ? 'T2 (%)' : 'T2');
  setHText('thT3', isPct ? 'T3 (%)' : 'T3');
  setHText('thT4', isPct ? 'T4 (%)' : 'T4');

  const regionalRow = allCities.find(c => c.tipo === 'TOTAL') || allCities[0];
  let listRows = allCities.filter(c => c.tipo === 'CIDADE');

  if(clusterFilter !== 'ALL') {
    listRows = listRows.filter(c => c.grupo === clusterFilter);
  }

  if(pickedCityId) {
    listRows = listRows.filter(c => c.id === pickedCityId);
  }

  listRows.sort((a, b) => {
    let va = a[currentSort.col];
    let vb = b[currentSort.col];
    if(va === null || va === undefined) va = -999999;
    if(vb === null || vb === undefined) vb = -999999;
    if(typeof va === 'string') {
      return currentSort.dir === 'asc' ? va.localeCompare(vb) : vb.localeCompare(va);
    }
    return currentSort.dir === 'asc' ? va - vb : vb - va;
  });

  const gmCities = listRows.filter(c => c.grupo === 'GM');
  const mdCities = listRows.filter(c => c.grupo === 'MD');

  const gmSubtotal = allCities.find(c => c.id === 'GM');
  const mdSubtotal = allCities.find(c => c.id === 'MD');

  const renderRow = (c, isSubtotal = false, isHeader = false, customLabel = null) => {
    const isPicked = (pickedCityId === c.id);
    let rowClass = '';
    if(isHeader) rowClass = 'section-divider-row';
    else if(isSubtotal) rowClass = 'row-subtotal';
    else if(isPicked) rowClass = 'row-picked';

    const baseReal = c.base_real || 1;
    const baseOrc = c.base_orc || baseReal;

    // Rates and comparative deltas in p.p.
    const taxaRealStr = c.taxa_real !== null && c.taxa_real !== undefined ? c.taxa_real.toFixed(2) + '%' : '--';
    const taxaOrcStr = c.taxa_orc !== null && c.taxa_orc !== undefined ? c.taxa_orc.toFixed(2) + '%' : '--';
    const taxaPpStr = c.taxa_delta_pp !== null && c.taxa_delta_pp !== undefined ? (c.taxa_delta_pp > 0 ? '+' : '') + c.taxa_delta_pp.toFixed(2) + ' p.p.' : '--';

    const taxaAgo = (c.vol_ago26 && baseReal > 0) ? (c.vol_ago26 / baseReal) * 100 : null;
    const momPp = (c.taxa_real !== null && taxaAgo !== null) ? (c.taxa_real - taxaAgo) : null;
    const taxaSep25 = (c.vol_sep25 && baseReal > 0) ? (c.vol_sep25 / baseReal) * 100 : null;
    const yoyPp = (c.taxa_real !== null && taxaSep25 !== null) ? (c.taxa_real - taxaSep25) : null;

    const ytdTaxa26 = (c.ytd_real && baseReal > 0) ? (c.ytd_real / 9 / baseReal) * 100 : null;
    const ytdTaxa25 = (c.ytd_2025 && baseReal > 0) ? (c.ytd_2025 / 9 / baseReal) * 100 : null;
    const ytdDeltaPp = (ytdTaxa26 !== null && ytdTaxa25 !== null) ? (ytdTaxa26 - ytdTaxa25) : null;
    const ytdTaxaOrc = (c.ytd_orc && baseOrc > 0) ? (c.ytd_orc / 9 / baseOrc) * 100 : null;
    const ytdRxoPp = (ytdTaxa26 !== null && ytdTaxaOrc !== null) ? (ytdTaxa26 - ytdTaxaOrc) : null;

    // Determine colors
    const rxoSign = (isPct ? (c.taxa_delta_pp || 0) : (c.rxo_delta || 0)) <= 0 ? 'color:var(--green);font-weight:600;' : 'color:var(--red);font-weight:600;';
    const momSign = (isPct ? (momPp || 0) : (c.mom_pct || 0)) < 0 ? 'color:var(--green);font-weight:600;' : 'color:var(--red);font-weight:600;';
    const yoySign = (isPct ? (yoyPp || 0) : (c.yoy_pct || 0)) < 0 ? 'color:var(--green);font-weight:600;' : 'color:var(--red);font-weight:600;';
    const ytd26x25Sign = (isPct ? (ytdDeltaPp || 0) : (c.ytd_26x25_pct || 0)) <= 0 ? 'color:var(--green);font-weight:600;' : 'color:var(--red);font-weight:600;';
    const taxaPpSign = (c.taxa_delta_pp || 0) <= 0 ? 'color:var(--green);font-weight:600;' : 'color:var(--red);font-weight:600;';

    // Cell values
    const colVolReal = isPct ? taxaRealStr : formatNum(c.vol_real, 0);
    const colVolOrc = isPct ? taxaOrcStr : (c.vol_orc ? formatNum(c.vol_orc, 0) : '--');
    const colRxoDelta = isPct ? taxaPpStr : (c.rxo_delta !== null && c.rxo_delta !== undefined ? (c.rxo_delta > 0 ? '+' : '') + formatNum(c.rxo_delta, 0) : '--');
    const colRxoPct = isPct ? taxaPpStr : formatPct(c.rxo_pct);
    const colMom = isPct ? (momPp !== null ? (momPp > 0 ? '+' : '') + momPp.toFixed(2) + ' p.p.' : '--') : formatPct(c.mom_pct);
    const colVolSep25 = isPct ? (taxaSep25 !== null ? taxaSep25.toFixed(2) + '%' : '--') : formatNum(c.vol_sep25, 0);
    const colYoy = isPct ? (yoyPp !== null ? (yoyPp > 0 ? '+' : '') + yoyPp.toFixed(2) + ' p.p.' : '--') : formatPct(c.yoy_pct);

    const colYtdReal = isPct ? (ytdTaxa26 !== null ? ytdTaxa26.toFixed(2) + '%' : '--') : formatNum(c.ytd_real, 0);
    const colYtd2025 = isPct ? (ytdTaxa25 !== null ? ytdTaxa25.toFixed(2) + '%' : '--') : formatNum(c.ytd_2025, 0);
    const colYtdDelta = isPct ? (ytdDeltaPp !== null ? (ytdDeltaPp > 0 ? '+' : '') + ytdDeltaPp.toFixed(2) + ' p.p.' : '--') : (c.ytd_26x25_delta !== null ? (c.ytd_26x25_delta > 0 ? '+' : '') + formatNum(c.ytd_26x25_delta, 0) : '--');
    const colYtdPct = isPct ? (ytdDeltaPp !== null ? (ytdDeltaPp > 0 ? '+' : '') + ytdDeltaPp.toFixed(2) + ' p.p.' : '--') : formatPct(c.ytd_26x25_pct);
    const colYtdOrc = isPct ? (ytdTaxaOrc !== null ? ytdTaxaOrc.toFixed(2) + '%' : '--') : (c.ytd_orc ? formatNum(c.ytd_orc, 0) : '--');
    const colYtdRxo = isPct ? (ytdRxoPp !== null ? (ytdRxoPp > 0 ? '+' : '') + ytdRxoPp.toFixed(2) + ' p.p.' : '--') : (c.ytd_rxo_pct !== null ? formatPct(c.ytd_rxo_pct) : '--');

    const colT1 = isPct ? ((c.t1 / baseReal) * 100).toFixed(2) + '%' : formatNum(c.t1, 0);
    const colT2 = isPct ? ((c.t2 / baseReal) * 100).toFixed(2) + '%' : formatNum(c.t2, 0);
    const colT3 = isPct ? ((c.t3 / baseReal) * 100).toFixed(2) + '%' : formatNum(c.t3, 0);
    const colT4 = isPct ? ((c.t4 / baseReal) * 100).toFixed(2) + '%' : formatNum(c.t4, 0);

    let nameContent = c.nome;
    if(isHeader) {
      const badgeCls = c.grupo ? c.grupo.toLowerCase() : 'gm';
      nameContent = `<span class="cluster-badge ${badgeCls}">${customLabel || c.nome}</span>`;
    } else if(isSubtotal) {
      nameContent = 'SUBTOTAL ' + c.nome.toUpperCase();
    }

    const rowClick = isHeader ? '' : `onclick="selectCity('${c.id}')" style="cursor:pointer;"`;

    return `<tr class="${rowClass}" ${rowClick}>
      <td class="l" style="font-weight:${isSubtotal || isHeader ? '700' : '600'};">${nameContent}</td>
      <td class="l">${c.uf}</td>
      <td class="col-sep">${formatNum(c.base_real, 0)}</td>
      <td>${c.base_orc ? formatNum(c.base_orc, 0) : '--'}</td>
      <td class="col-sep" style="font-weight:700;">${colVolReal}</td>
      <td>${colVolOrc}</td>
      <td style="${rxoSign}">${colRxoDelta}</td>
      <td style="${rxoSign}">${colRxoPct}</td>
      <td style="${momSign}">${colMom}</td>
      <td>${colVolSep25}</td>
      <td style="${yoySign}">${colYoy}</td>
      <td class="col-sep" style="font-weight:700;">${colYtdReal}</td>
      <td>${colYtd2025}</td>
      <td style="${ytd26x25Sign}">${colYtdDelta}</td>
      <td style="${ytd26x25Sign}">${colYtdPct}</td>
      <td>${colYtdOrc}</td>
      <td style="color:var(--ink2);">${colYtdRxo}</td>
      <td class="col-sep">${colT1}</td>
      <td>${colT2}</td>
      <td>${colT3}</td>
      <td style="font-weight:700;">${colT4}</td>
      <td class="col-sep" style="font-weight:700;">${taxaRealStr}</td>
      <td>${taxaOrcStr}</td>
      <td style="${taxaPpSign}">${taxaPpStr}</td>
    </tr>`;
  };

  let html = '';

  if(clusterFilter === 'ALL' || clusterFilter === 'GM') {
    if(gmSubtotal) {
      html += renderRow(gmSubtotal, false, true, 'Grandes Mercados (GM)');
    }
    gmCities.forEach(c => html += renderRow(c, false));
    if(gmSubtotal && clusterFilter !== 'GM') {
      html += renderRow(gmSubtotal, true);
    }
  }

  if(clusterFilter === 'ALL' || clusterFilter === 'MD') {
    if(mdSubtotal) {
      html += renderRow(mdSubtotal, false, true, 'Mercados em Desenvolvimento (MD)');
    }
    mdCities.forEach(c => html += renderRow(c, false));
    if(mdSubtotal && clusterFilter !== 'MD') {
      html += renderRow(mdSubtotal, true);
    }
  }

  tbody.innerHTML = html;

  if(regionalRow) {
    const r = regionalRow;
    const baseReal = r.base_real || 1;
    const baseOrc = r.base_orc || baseReal;

    const rTaxaRealStr = r.taxa_real !== null && r.taxa_real !== undefined ? r.taxa_real.toFixed(2) + '%' : '--';
    const rTaxaOrcStr = r.taxa_orc !== null && r.taxa_orc !== undefined ? r.taxa_orc.toFixed(2) + '%' : '--';
    const rTaxaPpStr = r.taxa_delta_pp !== null && r.taxa_delta_pp !== undefined ? (r.taxa_delta_pp > 0 ? '+' : '') + r.taxa_delta_pp.toFixed(2) + ' p.p.' : '--';

    const rTaxaAgo = (r.vol_ago26 && baseReal > 0) ? (r.vol_ago26 / baseReal) * 100 : null;
    const rMomPp = (r.taxa_real !== null && rTaxaAgo !== null) ? (r.taxa_real - rTaxaAgo) : null;
    const rTaxaSep25 = (r.vol_sep25 && baseReal > 0) ? (r.vol_sep25 / baseReal) * 100 : null;
    const rYoyPp = (r.taxa_real !== null && rTaxaSep25 !== null) ? (r.taxa_real - rTaxaSep25) : null;

    const rYtdTaxa26 = (r.ytd_real && baseReal > 0) ? (r.ytd_real / 9 / baseReal) * 100 : null;
    const rYtdTaxa25 = (r.ytd_2025 && baseReal > 0) ? (r.ytd_2025 / 9 / baseReal) * 100 : null;
    const rYtdDeltaPp = (rYtdTaxa26 !== null && rYtdTaxa25 !== null) ? (rYtdTaxa26 - rYtdTaxa25) : null;
    const rYtdTaxaOrc = (r.ytd_orc && baseOrc > 0) ? (r.ytd_orc / 9 / baseOrc) * 100 : null;
    const rYtdRxoPp = (rYtdTaxa26 !== null && rYtdTaxaOrc !== null) ? (rYtdTaxa26 - rYtdTaxaOrc) : null;

    const rRxoSign = (isPct ? (r.taxa_delta_pp || 0) : (r.rxo_delta || 0)) <= 0 ? 'color:var(--green);font-weight:700;' : 'color:var(--red);font-weight:700;';
    const rMomSign = (isPct ? (rMomPp || 0) : (r.mom_pct || 0)) < 0 ? 'color:var(--green);font-weight:700;' : 'color:var(--red);font-weight:700;';
    const rYoySign = (isPct ? (rYoyPp || 0) : (r.yoy_pct || 0)) < 0 ? 'color:var(--green);font-weight:700;' : 'color:var(--red);font-weight:700;';
    const rYtd26x25Sign = (isPct ? (rYtdDeltaPp || 0) : (r.ytd_26x25_pct || 0)) <= 0 ? 'color:var(--green);font-weight:700;' : 'color:var(--red);font-weight:700;';
    const rTaxaPpSign = (r.taxa_delta_pp || 0) <= 0 ? 'color:var(--green);font-weight:700;' : 'color:var(--red);font-weight:700;';

    const rColVolReal = isPct ? rTaxaRealStr : formatNum(r.vol_real, 0);
    const rColVolOrc = isPct ? rTaxaOrcStr : (r.vol_orc ? formatNum(r.vol_orc, 0) : '--');
    const rColRxoDelta = isPct ? rTaxaPpStr : (r.rxo_delta !== null && r.rxo_delta !== undefined ? (r.rxo_delta > 0 ? '+' : '') + formatNum(r.rxo_delta, 0) : '--');
    const rColRxoPct = isPct ? rTaxaPpStr : formatPct(r.rxo_pct);
    const rColMom = isPct ? (rMomPp !== null ? (rMomPp > 0 ? '+' : '') + rMomPp.toFixed(2) + ' p.p.' : '--') : formatPct(r.mom_pct);
    const rColVolSep25 = isPct ? (rTaxaSep25 !== null ? rTaxaSep25.toFixed(2) + '%' : '--') : formatNum(r.vol_sep25, 0);
    const rColYoy = isPct ? (rYoyPp !== null ? (rYoyPp > 0 ? '+' : '') + rYoyPp.toFixed(2) + ' p.p.' : '--') : formatPct(r.yoy_pct);

    const rColYtdReal = isPct ? (rYtdTaxa26 !== null ? rYtdTaxa26.toFixed(2) + '%' : '--') : formatNum(r.ytd_real, 0);
    const rColYtd2025 = isPct ? (rYtdTaxa25 !== null ? rYtdTaxa25.toFixed(2) + '%' : '--') : formatNum(r.ytd_2025, 0);
    const rColYtdDelta = isPct ? (rYtdDeltaPp !== null ? (rYtdDeltaPp > 0 ? '+' : '') + rYtdDeltaPp.toFixed(2) + ' p.p.' : '--') : (r.ytd_26x25_delta !== null ? (r.ytd_26x25_delta > 0 ? '+' : '') + formatNum(r.ytd_26x25_delta, 0) : '--');
    const rColYtdPct = isPct ? (rYtdDeltaPp !== null ? (rYtdDeltaPp > 0 ? '+' : '') + rYtdDeltaPp.toFixed(2) + ' p.p.' : '--') : formatPct(r.ytd_26x25_pct);
    const rColYtdOrc = isPct ? (rYtdTaxaOrc !== null ? rYtdTaxaOrc.toFixed(2) + '%' : '--') : (r.ytd_orc ? formatNum(r.ytd_orc, 0) : '--');
    const rColYtdRxo = isPct ? (rYtdRxoPp !== null ? (rYtdRxoPp > 0 ? '+' : '') + rYtdRxoPp.toFixed(2) + ' p.p.' : '--') : (r.ytd_rxo_pct !== null ? formatPct(r.ytd_rxo_pct) : '--');

    const rColT1 = isPct ? ((r.t1 / baseReal) * 100).toFixed(2) + '%' : formatNum(r.t1, 0);
    const rColT2 = isPct ? ((r.t2 / baseReal) * 100).toFixed(2) + '%' : formatNum(r.t2, 0);
    const rColT3 = isPct ? ((r.t3 / baseReal) * 100).toFixed(2) + '%' : formatNum(r.t3, 0);
    const rColT4 = isPct ? ((r.t4 / baseReal) * 100).toFixed(2) + '%' : formatNum(r.t4, 0);

    tfoot.innerHTML = `<tr>
      <td class="l" style="font-weight:800;">REGIONAL NORTE (TOTAL)</td>
      <td class="l">RNO</td>
      <td class="col-sep" style="font-weight:800;">${formatNum(r.base_real, 0)}</td>
      <td style="font-weight:700;">${r.base_orc ? formatNum(r.base_orc, 0) : '--'}</td>
      <td class="col-sep" style="font-weight:800; font-size:13px; color:var(--red);">${rColVolReal}</td>
      <td style="font-weight:700;">${rColVolOrc}</td>
      <td style="${rRxoSign}">${rColRxoDelta}</td>
      <td style="${rRxoSign}">${rColRxoPct}</td>
      <td style="${rMomSign}">${rColMom}</td>
      <td style="font-weight:700;">${rColVolSep25}</td>
      <td style="${rYoySign}">${rColYoy}</td>
      <td class="col-sep" style="font-weight:800;">${rColYtdReal}</td>
      <td style="font-weight:700;">${rColYtd2025}</td>
      <td style="${rYtd26x25Sign}">${rColYtdDelta}</td>
      <td style="${rYtd26x25Sign}">${rColYtdPct}</td>
      <td style="font-weight:700;">${rColYtdOrc}</td>
      <td style="font-weight:700;">${rColYtdRxo}</td>
      <td class="col-sep">${rColT1}</td>
      <td>${rColT2}</td>
      <td>${rColT3}</td>
      <td style="font-weight:800;">${rColT4}</td>
      <td class="col-sep" style="font-weight:800;">${rTaxaRealStr}</td>
      <td style="font-weight:700;">${rTaxaOrcStr}</td>
      <td style="${rTaxaPpSign}">${rTaxaPpStr}</td>
    </tr>`;
  }
}

function sortTable(col) {
  if(currentSort.col === col) {
    currentSort.dir = currentSort.dir === 'asc' ? 'desc' : 'asc';
  } else {
    currentSort.col = col;
    currentSort.dir = 'desc';
  }
  document.querySelectorAll('#tblMain thead th.sortable').forEach(th => {
    th.classList.remove('asc', 'desc');
  });
  renderTable();
}

function selectCity(cityId) {
  if(pickedCityId === cityId) {
    setCityFilter(null);
  } else {
    setCityFilter(cityId);
  }
}

/* =========================================================================
   TOOLTIPS & PINNING (Requisito 6 & 8)
   ========================================================================= */
const gtip = document.getElementById('gtip');

function showBubbleTip(e, jsonStr, force = false) {
  if(gtip.classList.contains('pinned') && !force) return;
  const d = JSON.parse(jsonStr);
  const isPct = (currentMetric === 'pct');

  let html = `<span class="gtip-close" onclick="unpinTip()" title="Fechar">×</span>`;
  html += `<b>${d.nome} (${d.uf})</b><br>`;
  html += `<span class="d">${d.grupo}</span><hr>`;

  if(isPct) {
    const rxoPp = d.taxa_delta_pp;
    const rxoColor = (rxoPp || 0) <= 0 ? 'ok' : 'bad';
    const momColor = (d.mom_pp || 0) < 0 ? 'ok' : 'bad';
    const yoyColor = (d.yoy_pp || 0) < 0 ? 'ok' : 'bad';

    html += `Taxa Real Set/26 (T4): <b>${d.taxa ? d.taxa.toFixed(2) + '%' : '--'}</b> (Base: ${formatNum(d.base, 0)})<br>`;
    html += `Taxa Orçada: <b>${d.taxa_orc ? d.taxa_orc.toFixed(2) + '%' : '--'}</b> (<span class="${rxoColor}">${rxoPp !== null && rxoPp !== undefined ? (rxoPp > 0 ? '+' : '') + rxoPp.toFixed(2) + ' p.p.' : '--'}</span> vs Orç)<br>`;
    html += `MoM (vs Ago/26): <span class="${momColor}">${d.mom_pp !== null && d.mom_pp !== undefined ? (d.mom_pp > 0 ? '+' : '') + d.mom_pp.toFixed(2) + ' p.p.' : '--'}</span><br>`;
    html += `YoY (vs Set/25): <span class="${yoyColor}">${d.yoy_pp !== null && d.yoy_pp !== undefined ? (d.yoy_pp > 0 ? '+' : '') + d.yoy_pp.toFixed(2) + ' p.p.' : '--'}</span><br>`;
  } else {
    const momColor = d.mom_pct < 0 ? 'ok' : 'bad';
    const yoyColor = d.yoy_pct < 0 ? 'ok' : 'bad';
    const rxoColor = d.rxo_delta <= 0 ? 'ok' : 'bad';

    html += `Volume Set/26 (T4): <b>${formatNum(d.vol, 0)} desc.</b><br>`;
    html += `Orçamento Mês: <b>${formatNum(d.orc, 0)} desc.</b> (<span class="${rxoColor}">${d.rxo_delta > 0 ? '+' : ''}${formatNum(d.rxo_delta, 0)}</span> | ${formatPct(d.rxo_pct)})<br>`;
    html += `MoM (vs Ago/26): <span class="${momColor}">${formatPct(d.mom_pct)}</span> (${d.mom_delta > 0 ? '+' : ''}${formatNum(d.mom_delta, 0)})<br>`;
    html += `YoY (vs Set/25): <span class="${yoyColor}">${formatPct(d.yoy_pct)}</span> (Base Set/25: ${formatNum(d.vol_sep25, 0)})<br>`;
    html += `Taxa de Churn: <b>${d.taxa ? d.taxa.toLocaleString('pt-BR', {minimumFractionDigits:2, maximumFractionDigits:2}) + '%' : '--'}</b><br>`;
  }
  html += `<div style="margin-top:6px; font-size:10px; color:#8fb3d9;">Clique para fixar este popup · Clique fora para fechar</div>`;

  gtip.innerHTML = html;
  gtip.style.display = 'block';
  positionTip(e, force);
}

function showTimelineTip(e, jsonStr, force = false) {
  if(gtip.classList.contains('pinned') && !force) return;
  const d = JSON.parse(jsonStr);
  const isPct = (currentMetric === 'pct');

  let html = `<span class="gtip-close" onclick="unpinTip()" title="Fechar">×</span>`;
  html += `<b>${d.mes}</b> (${d.iso}) · <span class="d">${d.escopo || 'Regional'}</span><hr>`;

  if(isPct) {
    html += `Taxa Realizada: <b style="color:#ff8b7d;">${d.realizado !== null && d.realizado !== undefined ? d.realizado.toFixed(2) + '%' : '--'}</b><br>`;
    if(d.orcamento !== null && d.orcamento !== undefined) {
      const deltaPp = d.realizado - d.orcamento;
      const deltaColor = deltaPp <= 0 ? 'ok' : 'bad';
      html += `Taxa Orçada: <b>${d.orcamento.toFixed(2)}%</b> (<span class="${deltaColor}">${deltaPp > 0 ? '+' : ''}${deltaPp.toFixed(2)} p.p.</span>)<br>`;
    }
    if(d.gm_real !== null && d.gm_real !== undefined) {
      html += `Grandes Mercados: <b>${d.gm_real.toFixed(2)}%</b><br>`;
    }
    if(d.md_real !== null && d.md_real !== undefined) {
      html += `Mercados em Desenv.: <b>${d.md_real.toFixed(2)}%</b><br>`;
    }
  } else {
    html += `Realizado Total: <b style="color:#ff8b7d;">${formatNum(d.realizado, 0)} desc.</b><br>`;
    if(d.orcamento) {
      const delta = d.realizado - d.orcamento;
      const deltaColor = delta <= 0 ? 'ok' : 'bad';
      html += `Orçamento: <b>${formatNum(d.orcamento, 0)} desc.</b> (<span class="${deltaColor}">${delta > 0 ? '+' : ''}${formatNum(delta, 0)}</span>)<br>`;
    }
    if(d.gm_real !== null && d.gm_real !== undefined) {
      html += `Grandes Mercados: <b>${formatNum(d.gm_real, 0)} desc.</b><br>`;
    }
    if(d.md_real !== null && d.md_real !== undefined) {
      html += `Mercados em Desenv.: <b>${formatNum(d.md_real, 0)} desc.</b><br>`;
    }
  }
  html += `<div style="margin-top:6px; font-size:10px; color:#8fb3d9;">Clique para fixar este popup · Clique fora para fechar</div>`;

  gtip.innerHTML = html;
  gtip.style.display = 'block';
  positionTip(e, force);
}

function showCcPointTip(e, jsonStr, force = false) {
  if(gtip.classList.contains('pinned') && !force) return;
  const d = JSON.parse(jsonStr);
  let html = `<span class="gtip-close" onclick="unpinTip()" title="Fechar">×</span>`;
  html += `<b>${d.motivo}</b> · ${d.mes}<hr>`;
  if(d.tipo === 'mix') {
    html += `Participação no Mix URA: <b style="color:#7fd6a0;">${d.mix}%</b><br>`;
    html += `<span class="d">Volume de ligações recebidas na retenção</span>`;
  } else {
    html += `Taxa de Geração de OS: <b style="color:#ff8b7d;">${d.taxa_os}%</b><br>`;
    html += `Taxa de Retenção / Reversão: <b style="color:#7fd6a0;">${d.retencao}%</b><br>`;
    html += `<span class="d">Conversão da demanda em ordem de serviço</span>`;
  }
  html += `<div style="margin-top:6px; font-size:10px; color:#8fb3d9;">Clique para fixar este popup · Clique fora para fechar</div>`;
  gtip.innerHTML = html;
  gtip.style.display = 'block';
  positionTip(e, force);
}

function showInvolPointTip(e, jsonStr, force = false) {
  if(gtip.classList.contains('pinned') && !force) return;
  const d = JSON.parse(jsonStr);
  let html = `<span class="gtip-close" onclick="unpinTip()" title="Fechar">×</span>`;
  html += `<b>${d.pilar}</b> · ${d.mes}<hr>`;
  html += `Volume: <b>${formatNum(d.valor, 0)} desc.</b><br>`;
  html += `Participação no Total: <b>${d.pct}%</b><br>`;
  html += `Total Involuntária do Mês: <span class="d">${formatNum(d.total, 0)} desc.</span>`;
  html += `<div style="margin-top:6px; font-size:10px; color:#8fb3d9;">Clique para fixar este popup · Clique fora para fechar</div>`;
  gtip.innerHTML = html;
  gtip.style.display = 'block';
  positionTip(e, force);
}

function showMonthTip(e, jsonStr, force = false) {
  if(gtip.classList.contains('pinned') && !force) return;
  const d = JSON.parse(jsonStr);
  let html = `<span class="gtip-close" onclick="unpinTip()" title="Fechar">×</span>`;
  html += `<b>${d.title}</b>`;
  if(d.subtitle) html += `<br><span class="d">${d.subtitle}</span>`;
  html += `<hr style="margin:5px 0; border:0; border-top:1px solid rgba(255,255,255,0.18);">`;
  // Requisito 6: overflow:visible (SEM barra de rolagem, mostra todos os dados)
  html += `<div style="overflow:visible;">`;
  d.items.forEach(it => {
    const dot = it.color ? `<span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:${it.color}; margin-right:6px;"></span>` : '';
    const note = it.note ? ` <span style="font-size:10px; color:#8fb3d9;">${it.note}</span>` : '';
    html += `<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:2px; font-size:11px;">
      <span>${dot}${it.label}</span>
      <span style="font-weight:700; margin-left:10px;">${it.val}${note}</span>
    </div>`;
  });
  html += `</div>`;
  if(d.footer) {
    html += `<hr style="margin:5px 0; border:0; border-top:1px solid rgba(255,255,255,0.18);">`;
    html += `<div style="font-size:10px; color:#8fb3d9;">${d.footer}</div>`;
  }
  html += `<div style="margin-top:6px; font-size:10px; color:#8fb3d9;">Clique para fixar este popup · Clique fora para fechar</div>`;
  gtip.innerHTML = html;
  gtip.style.display = 'block';
  positionTip(e, force);
}

function positionTip(e, force = false) {
  if(gtip.classList.contains('pinned') && !force) return;
  const tipW = gtip.offsetWidth || 340;
  const tipH = gtip.offsetHeight || 180;
  let x = e.clientX + 14;
  let y = e.clientY + 14;
  if(x + tipW > window.innerWidth - 12) {
    x = e.clientX - tipW - 14;
  }
  if(y + tipH > window.innerHeight - 12) {
    y = e.clientY - tipH - 14;
  }
  if(x < 10) x = 10;
  if(y < 10) y = 10;
  gtip.style.left = x + 'px';
  gtip.style.top = y + 'px';
}

function hideTip() {
  if(gtip.classList.contains('pinned')) return;
  gtip.style.display = 'none';
}

function unpinTip() {
  gtip.classList.remove('pinned');
  gtip.style.display = 'none';
}

function pinTip(e, jsonStr, type) {
  if(e && e.stopPropagation) e.stopPropagation();
  if(type === 'bubble') {
    showBubbleTip(e, jsonStr, true);
  } else if(type === 'timeline') {
    showTimelineTip(e, jsonStr, true);
  } else if(type === 'cc') {
    showCcPointTip(e, jsonStr, true);
  } else if(type === 'invol') {
    showInvolPointTip(e, jsonStr, true);
  } else {
    showMonthTip(e, jsonStr, true);
  }
  gtip.classList.add('pinned');
  gtip.style.display = 'block';
  positionTip(e, true);
}

function togglePinTip(e) {
  if(gtip.classList.contains('pinned')) {
    unpinTip();
  } else {
    gtip.classList.add('pinned');
    gtip.style.display = 'block';
  }
  if(e && e.stopPropagation) e.stopPropagation();
}

document.addEventListener('click', (e) => {
  if(gtip && gtip.classList.contains('pinned') && !gtip.contains(e.target)) {
    unpinTip();
  }
});

function exportTableCsv() {
  const modeData = RAW_DATA.modes[currentMode];
  let csv = 'Praça;UF;Cluster;Base_Real;Base_Orç;Realizado_T4;Orçado;Delta_RxO;Var_RxO_Pct;MoM_Pct;Set25;YoY_Pct;YTD_2026;YTD_2025;Delta_YTD_26x25;Var_YTD_26x25_Pct;YTD_Orçado;Delta_YTD_RxO_Pct;T1;T2;T3;T4;Taxa_Real_Pct;Taxa_Orç_Pct;Taxa_Delta_pp\\n';
  modeData.cities.forEach(c => {
    csv += `"${c.nome}";"${c.uf}";"${c.grupo}";${Math.round(c.base_real || 0)};${Math.round(c.base_orc || 0)};${Math.round(c.vol_real)};${Math.round(c.vol_orc || 0)};${Math.round(c.rxo_delta || 0)};${c.rxo_pct};${c.mom_pct};${Math.round(c.vol_sep25 || 0)};${c.yoy_pct};${Math.round(c.ytd_real)};${Math.round(c.ytd_2025 || 0)};${Math.round(c.ytd_26x25_delta || 0)};${c.ytd_26x25_pct};${Math.round(c.ytd_orc || 0)};${c.ytd_rxo_pct};${Math.round(c.t1)};${Math.round(c.t2)};${Math.round(c.t3)};${Math.round(c.t4)};${c.taxa_real};${c.taxa_orc};${c.taxa_delta_pp}\\n`;
  });
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `Churn_${currentMode}_${RAW_DATA.mes_referencia.replace(/ /g,'_')}.csv`;
  a.click();
}

function renderAll() {
  renderKPIs();
  renderCallcenterModule();
  renderInvoluntariaModule();
  renderScatterChart();
  renderTimelineChart();
  renderTable();
}

document.addEventListener('DOMContentLoaded', () => {
  renderAll();
});
