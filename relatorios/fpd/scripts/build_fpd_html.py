import json
import os

print("Lendo public/fpd_payload.json...")
with open('public/fpd_payload.json', 'r', encoding='utf-8') as f:
    payload_str = f.read()

payload = json.loads(payload_str)
print(f"Payload carregado: {payload['n']:,} contratos.")

html_template = """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1">
<title>Painel FPD — First Payment Default · Regional Norte | Pephub</title>
<meta name="description" content="Painel oficial de monitoramento de First Payment Default (FPD 30 e FPD 60) da Regional Norte (AM, PA, MA, AP, RR) — Safras Jan/26 a Mai/26.">
<style>
:root {
  --bg: #f4f5f7;
  --panel: #ffffff;
  --ink: #1c2430;
  --ink2: #5b6675;
  --ink3: #8b95a3;
  --line: #dfe3e8;
  --line2: #eceef1;
  --nav: #1b2430;
  --nav2: #27323f;
  --red: #c0392b;
  --red-bg: #fdf2f2;
  --amber: #c98a15;
  --amber-bg: #fef9ee;
  --green: #2f7d5d;
  --green-bg: #edf7f2;
  --blue: #2a5d8f;
  --blue-bg: #f0f5fa;
  --purple: #6b4b8a;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  background: var(--bg);
  color: var(--ink);
  font-size: 12px;
  line-height: 1.45;
  -webkit-font-smoothing: antialiased;
}
button, select, input { font-family: inherit; font-size: inherit; }

/* HEADER */
header {
  background: #fff;
  border-bottom: 1px solid var(--line);
  position: sticky;
  top: 0;
  z-index: 50;
  box-shadow: 0 1px 3px rgba(0,0,0,.04);
}
.hd-bar {
  background: linear-gradient(90deg, #8a0f18 0%, #c0191f 26%, #e23a1e 50%, #f47a1f 74%, #f9b233 100%);
  color: #fff;
  padding: 12px 24px;
  display: flex;
  align-items: center;
  gap: 14px;
}
.hd-ico {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 2px solid rgba(255,255,255,.9);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.hd-bar h1 {
  font-size: 18px;
  font-weight: 300;
  margin: 0;
  display: flex;
  align-items: baseline;
  gap: 8px;
}
.hd-bar h1 b { font-weight: 800; letter-spacing: -0.2px; }
.hd-bar h1 span { font-size: 13px; opacity: .92; font-weight: 400; }
.hd-sub {
  background: var(--nav);
  color: #c2c9d2;
  padding: 6px 24px;
  font-size: 11px;
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
.hd-sub b { color: #fff; }
.hd-sub .dot { width: 3px; height: 3px; background: #6b7785; border-radius: 50%; }
.hd-sub .hd-right { margin-left: auto; color: #8e9baa; font-weight: 600; }

.wrap {
  max-width: 1560px;
  margin: 0 auto;
  padding: 16px 20px 48px;
}

/* GAVETA DE FILTROS */
.filter-card {
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 4px;
  margin-bottom: 14px;
  overflow: hidden;
}
.f-toggle-bar {
  padding: 10px 14px;
  background: #fafbfc;
  border-bottom: 1px solid var(--line2);
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  user-select: none;
}
.f-toggle-left {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: var(--ink);
  font-size: 12px;
}
.f-chips {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  align-items: center;
}
.f-chip {
  background: var(--blue-bg);
  color: var(--blue);
  border: 1px solid rgba(42,93,143,.25);
  padding: 2px 7px;
  border-radius: 12px;
  font-size: 10.5px;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}
.f-chip span { cursor: pointer; opacity: .7; font-weight: bold; }
.f-chip span:hover { opacity: 1; }
.f-btn-clear {
  background: transparent;
  border: 1px solid var(--line);
  color: var(--ink2);
  padding: 3px 8px;
  border-radius: 3px;
  cursor: pointer;
  font-size: 11px;
}
.f-btn-clear:hover { background: #eee; }

.f-drawer {
  padding: 12px 14px;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 10px;
  background: #fff;
}
.f-grp {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.f-grp label {
  font-size: 10.5px;
  font-weight: 700;
  color: var(--ink2);
  text-transform: uppercase;
  letter-spacing: .4px;
}
.f-grp select {
  width: 100%;
  border: 1px solid var(--line);
  border-radius: 3px;
  padding: 5px 8px;
  background: #fff;
  color: var(--ink);
  outline: none;
  font-size: 11.5px;
}
.f-grp select:focus { border-color: var(--blue); }

/* KPIS */
.kpis {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 12px;
  margin-bottom: 14px;
}
.kpi {
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 4px;
  padding: 12px 14px;
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
.kpi .k {
  font-size: 10.5px;
  text-transform: uppercase;
  letter-spacing: .5px;
  font-weight: 700;
  color: var(--ink3);
  margin-bottom: 4px;
}
.kpi .v {
  font-size: 24px;
  font-weight: 700;
  letter-spacing: -0.5px;
  line-height: 1.1;
  margin-bottom: 4px;
}
.kpi .d {
  font-size: 11px;
  color: var(--ink2);
}
.kpi.red .v { color: var(--red); }
.kpi.amber .v { color: var(--amber); }
.kpi.green .v { color: var(--green); }
.kpi.blue .v { color: var(--blue); }
.kpi.purple .v { color: var(--purple); }

/* PAINEL */
.panel {
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 4px;
  margin-bottom: 14px;
  overflow: hidden;
}
.p-hd {
  padding: 10px 16px;
  border-bottom: 1px solid var(--line2);
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fafbfc;
}
.p-hd h2 {
  font-size: 12.5px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .5px;
  color: var(--ink);
  display: flex;
  align-items: center;
  gap: 8px;
}
.p-hd .note {
  font-size: 11px;
  color: var(--ink3);
  font-weight: 400;
  text-transform: none;
  letter-spacing: normal;
}
.hlp {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  border: 1px solid var(--line);
  background: #fff;
  color: var(--ink2);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: bold;
  cursor: pointer;
  margin-left: 6px;
}
.hlp:hover { background: #eef1f4; color: var(--ink); }

/* GRID GRAFICOS */
.grid-2 {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: 14px;
  margin-bottom: 14px;
}

/* MAPA CANVAS */
.maprow {
  display: grid;
  grid-template-columns: 1fr 340px;
  min-height: 560px;
}
#mapBox {
  position: relative;
  background: #e5eaed;
  overflow: hidden;
}
#mapCv {
  display: block;
  width: 100%;
  height: 560px;
  cursor: grab;
}
#mapCv.drag { cursor: grabbing; }
#mapCv.lasso { cursor: crosshair; }
.mapctl {
  position: absolute;
  top: 12px;
  left: 12px;
  background: rgba(255,255,255,.94);
  border: 1px solid var(--line);
  border-radius: 4px;
  padding: 8px 12px;
  box-shadow: 0 2px 6px rgba(0,0,0,.08);
  display: flex;
  flex-direction: column;
  gap: 6px;
  backdrop-filter: blur(4px);
  z-index: 5;
}
.map-tools {
  position: absolute;
  top: 12px;
  right: 12px;
  background: rgba(255,255,255,.94);
  border: 1px solid var(--line);
  border-radius: 4px;
  padding: 4px;
  box-shadow: 0 2px 6px rgba(0,0,0,.08);
  display: flex;
  gap: 4px;
  z-index: 5;
}
.map-btn {
  background: #fff;
  border: 1px solid var(--line);
  border-radius: 3px;
  padding: 4px 8px;
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
}
.map-btn:hover { background: #f0f2f5; }
.map-btn.on { background: var(--nav); color: #fff; border-color: var(--nav); }

.map-sidebar {
  border-left: 1px solid var(--line);
  background: #fafbfc;
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  overflow-y: auto;
  max-height: 560px;
}
.map-city-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 8px;
  background: #fff;
  border: 1px solid var(--line2);
  border-radius: 3px;
  cursor: pointer;
  transition: all .15s;
}
.map-city-row:hover { border-color: var(--blue); transform: translateX(2px); }

/* TABELA DE CONCENTRAÇÃO */
.tbl-wrap {
  overflow-x: auto;
  max-height: 480px;
  position: relative;
}
table.data-tbl {
  width: 100%;
  border-collapse: collapse;
  font-size: 11.5px;
}
table.data-tbl th {
  background: #fafbfc;
  border-bottom: 2px solid var(--line);
  padding: 8px 10px;
  text-align: left;
  font-weight: 700;
  color: var(--ink2);
  position: sticky;
  top: 0;
  z-index: 2;
  cursor: pointer;
  user-select: none;
}
table.data-tbl th.num { text-align: right; }
table.data-tbl td {
  padding: 6px 10px;
  border-bottom: 1px solid var(--line2);
  color: var(--ink);
}
table.data-tbl td.num { text-align: right; font-variant-numeric: tabular-nums; }
table.data-tbl tr:hover td { background: #f4f7fb; }
.tabs-bar {
  display: flex;
  gap: 2px;
  background: #eceef1;
  padding: 3px;
  border-radius: 4px;
}
.tab-b {
  background: transparent;
  border: none;
  padding: 5px 12px;
  border-radius: 3px;
  font-size: 11px;
  font-weight: 600;
  color: var(--ink2);
  cursor: pointer;
}
.tab-b.on { background: #fff; color: var(--ink); box-shadow: 0 1px 2px rgba(0,0,0,.08); }

.bar-cell {
  position: relative;
  display: inline-block;
  width: 60px;
  height: 8px;
  background: #eceef1;
  border-radius: 4px;
  overflow: hidden;
  vertical-align: middle;
  margin-right: 6px;
}
.bar-fill {
  height: 100%;
  border-radius: 4px;
}

/* MODAL */
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(18,24,32,.55);
  display: none;
  align-items: center;
  justify-content: center;
  z-index: 100;
  backdrop-filter: blur(2px);
}
.modal-overlay.open { display: flex; }
.modal-box {
  background: #fff;
  border-radius: 6px;
  max-width: 520px;
  width: 90%;
  box-shadow: 0 10px 25px rgba(0,0,0,.2);
  overflow: hidden;
}
.modal-hd {
  padding: 12px 16px;
  background: #fafbfc;
  border-bottom: 1px solid var(--line);
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.modal-hd h3 { font-size: 13px; font-weight: 700; color: var(--ink); }
.modal-close {
  background: none; border: none; font-size: 16px; cursor: pointer; color: var(--ink3);
}
.modal-bd {
  padding: 16px;
  font-size: 12px;
  line-height: 1.6;
  color: var(--ink2);
}

@media(max-width: 1024px) {
  .kpis { grid-template-columns: repeat(2, 1fr); }
  .grid-2 { grid-template-columns: 1fr; }
  .maprow { grid-template-columns: 1fr; }
}
</style>
</head>
<body>

<header>
  <div class="hd-bar">
    <div class="hd-ico">
      <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#fff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
        <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
        <line x1="16" y1="2" x2="16" y2="6"/>
        <line x1="8" y1="2" x2="8" y2="6"/>
        <line x1="3" y1="10" x2="21" y2="10"/>
      </svg>
    </div>
    <h1><b>Pephub</b> <span>Painel FPD — First Payment Default · Regional Norte</span></h1>
    <div style="margin-left:auto; display:flex; gap:8px;">
      <a href="../" style="color:#fff; text-decoration:none; background:rgba(255,255,255,.15); padding:5px 12px; border-radius:3px; font-weight:600; font-size:11px; border:1px solid rgba(255,255,255,.3);">← Voltar ao Portal</a>
    </div>
  </div>
  <div class="hd-sub">
    <span><b>Pephub</b></span>
    <span class="dot"></span>
    <span>Painel de Qualidade de Venda & Primeiro Pagamento</span>
    <span class="dot"></span>
    <span>Regional Norte (AM · PA · MA · AP · RR)</span>
    <span class="dot"></span>
    <span>Safras Jan/26 a Mai/26</span>
    <span class="hd-right">Posição Oficial</span>
  </div>
</header>

<div class="wrap">

  <!-- FILTROS -->
  <div class="filter-card">
    <div class="f-toggle-bar" id="fToggleBar">
      <div class="f-toggle-left">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></svg>
        <span>Filtros Globais</span>
        <div class="f-chips" id="activeChips"></div>
      </div>
      <div style="display:flex; gap:8px; align-items:center;">
        <button class="f-btn-clear" id="btnClearFilters">Limpar Filtros</button>
        <span style="font-size:10px; color:var(--ink3);" id="drawerArrow">▼</span>
      </div>
    </div>
    <div class="f-drawer" id="fDrawer">
      <div class="f-grp">
        <label>Safra</label>
        <select id="fltSafra"><option value="">Todas as Safras (Jan–Mai/26)</option></select>
      </div>
      <div class="f-grp">
        <label>UF</label>
        <select id="fltUf"><option value="">Todas as UFs</option></select>
      </div>
      <div class="f-grp">
        <label>Cidade</label>
        <select id="fltCidade"><option value="">Todas as Cidades</option></select>
      </div>
      <div class="f-grp">
        <label>Canal de Venda</label>
        <select id="fltCanal"><option value="">Todos os Canais</option></select>
      </div>
      <div class="f-grp">
        <label>Forma de Pagamento</label>
        <select id="fltPagto"><option value="">Todas as Formas</option></select>
      </div>
      <div class="f-grp">
        <label>Faixa de Risco (Score)</label>
        <select id="fltRisco"><option value="">Todas as Faixas</option></select>
      </div>
    </div>
  </div>

  <!-- KPIS -->
  <div class="kpis">
    <div class="kpi blue">
      <div class="k">Instalações Analisadas <button class="hlp" data-h="inst">?</button></div>
      <div class="v" id="kpiInst">0</div>
      <div class="d" id="kpiInstSub">Denominador oficial</div>
    </div>
    <div class="kpi red">
      <div class="k">Taxa FPD 60 (Oficial) <button class="hlp" data-h="fpd60">?</button></div>
      <div class="v" id="kpiFpd60">0,00%</div>
      <div class="d" id="kpiFpd60Sub">0 contratos (1ª fatura cheia)</div>
    </div>
    <div class="kpi amber">
      <div class="k">Taxa FPD 30 (Pró-rata) <button class="hlp" data-h="fpd30">?</button></div>
      <div class="v" id="kpiFpd30">0,00%</div>
      <div class="d" id="kpiFpd30Sub">0 contratos (1ª parcial)</div>
    </div>
    <div class="kpi green">
      <div class="k">Adimplência 1ª Fatura <button class="hlp" data-h="adimp">?</button></div>
      <div class="v" id="kpiAdimp">0,00%</div>
      <div class="d" id="kpiAdimpSub">0 contratos em dia</div>
    </div>
    <div class="kpi purple">
      <div class="k">Inadimplência Crônica (Aging 90+) <button class="hlp" data-h="aging90">?</button></div>
      <div class="v" id="kpiOver90">0,00%</div>
      <div class="d" id="kpiOver90Sub">0 contratos com 90d+</div>
    </div>
  </div>

  <!-- GRAFICOS SUPERIORES -->
  <div class="grid-2">
    <!-- EVOLUCAO TEMPORAL POR SAFRA -->
    <div class="panel">
      <div class="p-hd">
        <h2>Evolução do FPD por Safra de Instalação <span class="note">(Jan/26 a Mai/26)</span> <button class="hlp" data-h="grafSafra">?</button></h2>
      </div>
      <div style="padding:16px;" id="chartSafraBox">
        <svg id="svgSafra" width="100%" height="240" viewBox="0 0 600 240"></svg>
      </div>
    </div>

    <!-- CANAL E FORMA DE PAGAMENTO -->
    <div class="panel">
      <div class="p-hd">
        <h2>FPD 60 por Canal & Forma de Pagamento <button class="hlp" data-h="grafCanal">?</button></h2>
      </div>
      <div style="padding:16px;" id="chartCanalBox">
        <svg id="svgCanal" width="100%" height="240" viewBox="0 0 450 240"></svg>
      </div>
    </div>
  </div>

  <!-- VISÃO GEOESPACIAL / MAPA -->
  <div class="panel">
    <div class="p-hd">
      <h2>Visão Geoespacial da Inadimplência FPD <span class="note">(Mapa Interativo de Densidade & Contratos)</span> <button class="hlp" data-h="mapa">?</button></h2>
      <div style="display:flex; gap:6px; align-items:center;">
        <span style="font-size:11px; color:var(--ink3);">Camada:</span>
        <select id="mapLayerSelect" style="padding:3px 6px; border:1px solid var(--line); border-radius:3px;">
          <option value="heat">Mapa de Calor (Densidade FPD 60)</option>
          <option value="cells" selected>Células de Concentração</option>
          <option value="points">Pontos Individuais</option>
        </select>
      </div>
    </div>
    <div class="maprow">
      <div id="mapBox">
        <canvas id="mapCv"></canvas>
        <div class="mapctl">
          <div style="font-size:10.5px; font-weight:700; color:var(--ink2); text-transform:uppercase;">Legenda Semântica</div>
          <div style="display:flex; align-items:center; gap:6px; font-size:11px;">
            <div style="width:10px; height:10px; background:#c0392b; border-radius:50%;"></div>
            <span>FPD 60 (1ª Cheia Inadimplente)</span>
          </div>
          <div style="display:flex; align-items:center; gap:6px; font-size:11px;">
            <div style="width:10px; height:10px; background:#f59e0b; border-radius:50%;"></div>
            <span>FPD 30 (Pró-rata Inadimplente)</span>
          </div>
          <div style="display:flex; align-items:center; gap:6px; font-size:11px;">
            <div style="width:10px; height:10px; background:#2f7d5d; border-radius:50%;"></div>
            <span>Em Dia (Adimplente)</span>
          </div>
        </div>
        <div class="map-tools">
          <button class="map-btn" id="btnZoomIn" title="Aproximar">+</button>
          <button class="map-btn" id="btnZoomOut" title="Afastar">−</button>
          <button class="map-btn" id="btnResetMap" title="Resetar visualização">⟲</button>
          <button class="map-btn" id="btnLasso" title="Ferramenta de Laço Livre para seleção">⚲ Laço</button>
        </div>
      </div>
      <div class="map-sidebar">
        <div style="font-size:11px; font-weight:700; text-transform:uppercase; color:var(--ink2);">Concentração por Praça</div>
        <div id="mapCitiesList" style="display:flex; flex-direction:column; gap:6px;"></div>
      </div>
    </div>
  </div>

  <!-- TABELA DE CONCENTRAÇÃO -->
  <div class="panel">
    <div class="p-hd">
      <div style="display:flex; align-items:center; gap:14px;">
        <h2>Matriz de Concentração de Vendas <button class="hlp" data-h="tabela">?</button></h2>
        <div class="tabs-bar" id="tblTabs">
          <button class="tab-b on" data-dim="parceiro">Por Parceiro</button>
          <button class="tab-b" data-dim="vendedor">Por Vendedor</button>
          <button class="tab-b" data-dim="cidade">Por Cidade</button>
          <button class="tab-b" data-dim="canal">Por Canal</button>
        </div>
      </div>
      <div style="display:flex; align-items:center; gap:8px;">
        <input type="text" id="tblSearch" placeholder="Buscar parceiro, vendedor ou cidade..." style="padding:4px 8px; border:1px solid var(--line); border-radius:3px; width:220px;">
        <button class="map-btn" id="btnExportCsv" style="background:#2a5d8f; color:#fff; border-color:#2a5d8f;">Exportar CSV</button>
      </div>
    </div>
    <div class="tbl-wrap">
      <table class="data-tbl" id="mainTable">
        <thead>
          <tr id="tblHead">
            <th>Nome</th>
            <th class="num">Instalações</th>
            <th class="num">FPD 60 (Oficial)</th>
            <th class="num">Taxa FPD 60</th>
            <th class="num">FPD 30</th>
            <th class="num">Taxa FPD 30</th>
            <th class="num">Em Dia (%)</th>
          </tr>
        </thead>
        <tbody id="tblBody"></tbody>
      </table>
    </div>
  </div>

</div>

<!-- MODAL DE AJUDA -->
<div class="modal-overlay" id="helpModal">
  <div class="modal-box">
    <div class="modal-hd">
      <h3 id="modalTitle">Ajuda e Glossário de Métricas</h3>
      <button class="modal-close" id="modalClose">✕</button>
    </div>
    <div class="modal-bd" id="modalText"></div>
  </div>
</div>

<script>
// PAYLOAD EMBUTIDO EM BASE64
const PAYLOAD = """ + payload_str + """;

// GLOSSÁRIO DE AJUDA
const HELP = {
  inst: "<b>Instalações Analisadas (Denominador):</b> Representa o volume total de contratos habilitados e instalados nas safras de Janeiro a Maio de 2026 na Regional Norte.",
  fpd60: "<b>FPD 60 (First Payment Default - 1ª Fatura Cheia):</b> Indicador oficial de qualidade de venda da Claro. Considera contratos que não realizaram o pagamento da primeira fatura de ciclo cheio (Aging 60). Período sob rigoroso acompanhamento da responsabilidade da venda.",
  fpd30: "<b>FPD 30 (Pró-rata):</b> Inadimplência da primeira cobrança proporcional emitida após a instalação. Sinaliza desvios de onboarding precoce ou não entrega do serviço.",
  adimp: "<b>Adimplência 1ª Fatura (Em Dia):</b> Percentual de contratos que honraram integralmente os pagamentos iniciais sem gerar bloqueio ou atraso.",
  aging90: "<b>Inadimplência Crônica (Aging 90+):</b> Clientes com faturas acumuladas acima de 90 dias de vencimento, com alta propensão a corte definitivo e perda irreversível.",
  grafSafra: "<b>Curva por Safra:</b> Demonstra a evolução mês a mês das safras de instalação. O volume de vendas é representado pelas colunas e a curva de inadimplência FPD 60 pela linha vermelha.",
  grafCanal: "<b>Performance por Canal:</b> Compara a taxa de FPD entre canais presenciais (Lojas, PAP) e remotos/eletrônicos, além de contrastar a adimplência de clientes com débito em conta versus boleto.",
  mapa: "<b>Visão Geoespacial (Canvas):</b> Mapeamento cartográfico por Projeção Web Mercator. Exibe a distribuição espacial das instalações e inadimplência. Utilize a ferramenta de Laço Livre para selecionar polígonos no mapa.",
  tabela: "<b>Matriz de Concentração:</b> Tabela dinâmica para auditoria de parceiros, equipes e vendedores com maiores taxas de inadimplência. Clique em qualquer cabeçalho para ordenar."
};

// ESTADO GLOBAL DO DASHBOARD
let C = {};
const D = PAYLOAD.dicts;
const N = PAYLOAD.n;
const BBOX = PAYLOAD.bbox; // [min_lat, max_lat, min_lon, max_lon]

let sel = {
  safra: new Set(),
  uf: new Set(),
  cidade: new Set(),
  canal: new Set(),
  pagto: new Set(),
  risco: new Set()
};

let currentTab = 'parceiro';
let sortCol = 'fpd60_pct';
let sortAsc = false;
let lassoPolygon = null;
let isLassoActive = false;

// DESCOMPACTAÇÃO DE COLUNAS
async function inflate(b64) {
  const bin = atob(b64);
  const bytes = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
  const stream = new Response(bytes).body.pipeThrough(new DecompressionStream('deflate'));
  return new Response(stream).arrayBuffer();
}


async function initData() {
  for (const k in PAYLOAD.cols) {
    const colObj = PAYLOAD.cols[k];
    const ab = await inflate(colObj.b);
    C[k] = colObj.t === 'u8' ? new Uint8Array(ab) : new Uint16Array(ab);
  }
  setupUI();
  setupMap();
  render();
}

// SETUP DA INTERFACE
function setupUI() {
  // Popular Selects de Filtros
  populateSelect('fltSafra', D.safra);
  populateSelect('fltUf', D.uf);
  populateSelect('fltCidade', D.cidade);
  populateSelect('fltCanal', D.canal_grupo);
  populateSelect('fltPagto', D.pagto);
  populateSelect('fltRisco', D.risco);

  // Toggle Drawer
  document.getElementById('fToggleBar').onclick = (e) => {
    if (e.target.closest('#btnClearFilters') || e.target.closest('.f-chip')) return;
    const dr = document.getElementById('fDrawer');
    const isHidden = dr.style.display === 'none';
    dr.style.display = isHidden ? 'grid' : 'none';
    document.getElementById('drawerArrow').textContent = isHidden ? '▲' : '▼';
  };

  // Eventos de Filtro
  ['fltSafra', 'fltUf', 'fltCidade', 'fltCanal', 'fltPagto', 'fltRisco'].forEach(id => {
    document.getElementById(id).onchange = () => {
      readFilters();
      render();
    };
  });

  document.getElementById('btnClearFilters').onclick = () => {
    ['fltSafra', 'fltUf', 'fltCidade', 'fltCanal', 'fltPagto', 'fltRisco'].forEach(id => {
      document.getElementById(id).value = '';
    });
    lassoPolygon = null;
    readFilters();
    render();
  };

  // Abas da Tabela
  document.getElementById('tblTabs').onclick = (e) => {
    if (e.target.classList.contains('tab-b')) {
      document.querySelectorAll('#tblTabs .tab-b').forEach(b => b.classList.remove('on'));
      e.target.classList.add('on');
      currentTab = e.target.dataset.dim;
      renderTable();
    }
  };

  // Busca na Tabela
  document.getElementById('tblSearch').oninput = () => {
    renderTable();
  };

  // Exportar CSV
  document.getElementById('btnExportCsv').onclick = exportTableCsv;

  // Modais de Ajuda
  document.querySelectorAll('.hlp').forEach(btn => {
    btn.onclick = (e) => {
      e.stopPropagation();
      const hKey = btn.dataset.h;
      if (HELP[hKey]) {
        document.getElementById('modalTitle').textContent = btn.parentElement.textContent.replace('?', '').trim();
        document.getElementById('modalText').innerHTML = HELP[hKey];
        document.getElementById('helpModal').classList.add('open');
      }
    };
  });

  document.getElementById('modalClose').onclick = () => {
    document.getElementById('helpModal').classList.remove('open');
  };
  document.getElementById('helpModal').onclick = (e) => {
    if (e.target === document.getElementById('helpModal')) {
      document.getElementById('helpModal').classList.remove('open');
    }
  };
}

function populateSelect(id, items) {
  const selEl = document.getElementById(id);
  items.forEach((item, idx) => {
    const opt = document.createElement('option');
    opt.value = idx;
    opt.textContent = item;
    selEl.appendChild(opt);
  });
}

function readFilters() {
  sel.safra.clear();
  sel.uf.clear();
  sel.cidade.clear();
  sel.canal.clear();
  sel.pagto.clear();
  sel.risco.clear();

  const getV = (id) => document.getElementById(id).value;
  if (getV('fltSafra') !== '') sel.safra.add(parseInt(getV('fltSafra')));
  if (getV('fltUf') !== '') sel.uf.add(parseInt(getV('fltUf')));
  if (getV('fltCidade') !== '') sel.cidade.add(parseInt(getV('fltCidade')));
  if (getV('fltCanal') !== '') sel.canal.add(parseInt(getV('fltCanal')));
  if (getV('fltPagto') !== '') sel.pagto.add(parseInt(getV('fltPagto')));
  if (getV('fltRisco') !== '') sel.risco.add(parseInt(getV('fltRisco')));

  renderChips();
}

function renderChips() {
  const box = document.getElementById('activeChips');
  box.innerHTML = '';

  const addChip = (label, removeFn) => {
    const chip = document.createElement('div');
    chip.className = 'f-chip';
    chip.innerHTML = `${label} <span title="Remover">✕</span>`;
    chip.querySelector('span').onclick = removeFn;
    box.appendChild(chip);
  };

  if (sel.safra.size > 0) sel.safra.forEach(v => addChip(`Safra: ${D.safra[v]}`, () => { document.getElementById('fltSafra').value = ''; readFilters(); render(); }));
  if (sel.uf.size > 0) sel.uf.forEach(v => addChip(`UF: ${D.uf[v]}`, () => { document.getElementById('fltUf').value = ''; readFilters(); render(); }));
  if (sel.cidade.size > 0) sel.cidade.forEach(v => addChip(`Cidade: ${D.cidade[v]}`, () => { document.getElementById('fltCidade').value = ''; readFilters(); render(); }));
  if (sel.canal.size > 0) sel.canal.forEach(v => addChip(`Canal: ${D.canal_grupo[v]}`, () => { document.getElementById('fltCanal').value = ''; readFilters(); render(); }));
  if (sel.pagto.size > 0) sel.pagto.forEach(v => addChip(`Pagto: ${D.pagto[v]}`, () => { document.getElementById('fltPagto').value = ''; readFilters(); render(); }));
  if (sel.risco.size > 0) sel.risco.forEach(v => addChip(`Score: ${D.risco[v]}`, () => { document.getElementById('fltRisco').value = ''; readFilters(); render(); }));
  if (lassoPolygon) addChip(`Área Geográfica (Laço) ⚲`, () => { lassoPolygon = null; render(); });
}

// FILTRAGEM ULTRA-RÁPIDA (Vetor de Booleanos)
let activeRows = new Uint8Array(N);

function applyFilters() {
  const hasSafra = sel.safra.size > 0;
  const hasUf = sel.uf.size > 0;
  const hasCid = sel.cidade.size > 0;
  const hasCanal = sel.canal.size > 0;
  const hasPagto = sel.pagto.size > 0;
  const hasRisco = sel.risco.size > 0;
  const hasLasso = lassoPolygon !== null && lassoPolygon.length > 2;

  let count = 0;
  for (let i = 0; i < N; i++) {
    if (hasSafra && !sel.safra.has(C.safra[i])) { activeRows[i] = 0; continue; }
    if (hasUf && !sel.uf.has(C.uf[i])) { activeRows[i] = 0; continue; }
    if (hasCid && !sel.cidade.has(C.cidade[i])) { activeRows[i] = 0; continue; }
    if (hasCanal && !sel.canal.has(C.canal[i])) { activeRows[i] = 0; continue; }
    if (hasPagto && !sel.pagto.has(C.pagto[i])) { activeRows[i] = 0; continue; }
    if (hasRisco && !sel.risco.has(C.risco[i])) { activeRows[i] = 0; continue; }

    if (hasLasso) {
      const px = C.gx[i], py = C.gy[i];
      if (!pointInPolygon(px, py, lassoPolygon)) { activeRows[i] = 0; continue; }
    }

    activeRows[i] = 1;
    count++;
  }
  return count;
}

function pointInPolygon(x, y, vs) {
  let inside = false;
  for (let i = 0, j = vs.length - 1; i < vs.length; j = i++) {
    const xi = vs[i][0], yi = vs[i][1];
    const xj = vs[j][0], yj = vs[j][1];
    const intersect = ((yi > y) !== (yj > y)) && (x < (xj - xi) * (y - yi) / (yj - yi) + xi);
    if (intersect) inside = !inside;
  }
  return inside;
}

// RENDERIZAÇÃO GERAL
function render() {
  const visCount = applyFilters();
  renderKPIs(visCount);
  renderSafraChart();
  renderCanalChart();
  renderTable();
  drawMap();
}

function fmt(n) {
  return new Intl.NumberFormat('pt-BR').format(n);
}

function pct(n, total) {
  if (!total || total === 0) return '0,00%';
  return (n / total * 100).toFixed(2).replace('.', ',') + '%';
}

function renderKPIs(total) {
  let ag30 = 0, ag60 = 0, ag90 = 0;
  for (let i = 0; i < N; i++) {
    if (!activeRows[i]) continue;
    if (C.ag30[i]) ag30++;
    if (C.ag60[i]) ag60++;
    if (C.ag90[i] || C.ag120[i] || C.ag150[i] || C.ag180[i] || C.over90[i]) ag90++;
  }
  const emDia = total - ag60;

  document.getElementById('kpiInst').textContent = fmt(total);
  document.getElementById('kpiFpd60').textContent = pct(ag60, total);
  document.getElementById('kpiFpd60Sub').textContent = `${fmt(ag60)} contratos (1ª fatura cheia)`;

  document.getElementById('kpiFpd30').textContent = pct(ag30, total);
  document.getElementById('kpiFpd30Sub').textContent = `${fmt(ag30)} contratos (1ª parcial)`;

  document.getElementById('kpiAdimp').textContent = pct(emDia, total);
  document.getElementById('kpiAdimpSub').textContent = `${fmt(emDia)} contratos em dia`;

  document.getElementById('kpiOver90').textContent = pct(ag90, total);
  document.getElementById('kpiOver90Sub').textContent = `${fmt(ag90)} contratos inadimplentes 90d+`;
}

// GRÁFICO 1: EVOLUÇÃO POR SAFRA (SVG)
function renderSafraChart() {
  const svg = document.getElementById('svgSafra');
  const safraStats = D.safra.map((lbl, idx) => ({ idx, lbl, total: 0, ag60: 0, ag30: 0 }));

  for (let i = 0; i < N; i++) {
    if (!activeRows[i]) continue;
    const s = C.safra[i];
    safraStats[s].total++;
    if (C.ag60[i]) safraStats[s].ag60++;
    if (C.ag30[i]) safraStats[s].ag30++;
  }

  const maxTot = Math.max(...safraStats.map(s => s.total), 1);
  const W = 600, H = 240, padL = 50, padR = 40, padT = 30, padB = 40;
  const chartW = W - padL - padR, chartH = H - padT - padB;
  const colW = chartW / safraStats.length;

  let h = '';
  // Linhas de Grade
  for (let g = 0; g <= 4; g++) {
    const y = padT + (chartH / 4) * g;
    const val = Math.round(maxTot * (1 - g / 4));
    h += `<line x1="${padL}" y1="${y}" x2="${W - padR}" y2="${y}" stroke="#eceef1" stroke-width="1"/>`;
    h += `<text x="${padL - 8}" y="${y + 4}" font-size="10" fill="#8b95a3" text-anchor="end">${fmt(val)}</text>`;
  }

  // Barras de Volume
  safraStats.forEach((st, idx) => {
    const x = padL + idx * colW + colW * 0.2;
    const bw = colW * 0.6;
    const bh = (st.total / maxTot) * chartH;
    const y = padT + chartH - bh;
    const isFiltered = sel.safra.has(st.idx);

    h += `<rect x="${x}" y="${y}" width="${bw}" height="${bh}" fill="${isFiltered ? '#1b2430' : '#d2d8e0'}" rx="3" style="cursor:pointer" onclick="toggleFilterSafra(${st.idx})"/>`;
    h += `<text x="${x + bw/2}" y="${y - 6}" font-size="10" font-weight="700" fill="#5b6675" text-anchor="middle">${fmt(st.total)}</text>`;
    h += `<text x="${x + bw/2}" y="${H - 15}" font-size="11" font-weight="600" fill="${isFiltered ? '#1b2430' : '#5b6675'}" text-anchor="middle">${st.lbl}</text>`;
  });

  // Linhas de Taxa FPD 60 (Vermelha)
  const pts60 = safraStats.map((st, idx) => {
    const x = padL + idx * colW + colW * 0.5;
    const rate = st.total > 0 ? (st.ag60 / st.total) : 0;
    const y = padT + chartH - (rate / 0.5) * chartH; // escala 0 a 50%
    return { x, y: Math.max(padT, Math.min(padT + chartH, y)), rate: rate * 100 };
  });

  if (pts60.length > 1) {
    const pathD = pts60.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ');
    h += `<path d="${pathD}" fill="none" stroke="#c0392b" stroke-width="2.6" stroke-linecap="round"/>`;
    pts60.forEach(p => {
      h += `<circle cx="${p.x}" cy="${p.y}" r="4" fill="#fff" stroke="#c0392b" stroke-width="2.5"/>`;
      h += `<text x="${p.x}" y="${p.y - 8}" font-size="10" font-weight="800" fill="#c0392b" text-anchor="middle" stroke="#fff" stroke-width="3" paint-order="stroke fill">${p.rate.toFixed(1)}%</text>`;
    });
  }

  svg.innerHTML = h;
}

window.toggleFilterSafra = function(idx) {
  if (sel.safra.has(idx)) sel.safra.delete(idx);
  else sel.safra.add(idx);
  document.getElementById('fltSafra').value = sel.safra.size === 1 ? [...sel.safra][0] : '';
  render();
};

// GRÁFICO 2: CANAL E FORMA DE PAGAMENTO (SVG)
function renderCanalChart() {
  const svg = document.getElementById('svgCanal');
  const canalStats = D.canal_grupo.map((lbl, idx) => ({ lbl, total: 0, ag60: 0 }));

  for (let i = 0; i < N; i++) {
    if (!activeRows[i]) continue;
    const c = C.canal[i];
    canalStats[c].total++;
    if (C.ag60[i]) canalStats[c].ag60++;
  }

  // Filtrar os 5 maiores canais
  const topCanais = canalStats.filter(c => c.total > 0).sort((a,b) => b.total - a.total).slice(0, 5);
  const W = 450, H = 240, rowH = 34, padL = 110, padR = 60, padT = 20;

  let h = '';
  topCanais.forEach((c, idx) => {
    const y = padT + idx * rowH;
    const rate = c.total > 0 ? (c.ag60 / c.total * 100) : 0;
    const maxBarW = W - padL - padR;
    const barW = Math.min(maxBarW, (rate / 45) * maxBarW); // max 45%

    h += `<text x="${padL - 8}" y="${y + 14}" font-size="11" font-weight="600" fill="#1c2430" text-anchor="end">${c.lbl.length > 14 ? c.lbl.slice(0,14)+'…' : c.lbl}</text>`;
    h += `<rect x="${padL}" y="${y + 4}" width="${maxBarW}" height="12" fill="#eceef1" rx="2"/>`;
    h += `<rect x="${padL}" y="${y + 4}" width="${barW}" height="12" fill="${rate > 25 ? '#c0392b' : (rate > 18 ? '#c98a15' : '#2f7d5d')}" rx="2"/>`;
    h += `<text x="${padL + barW + 6}" y="${y + 14}" font-size="10.5" font-weight="700" fill="#1c2430">${rate.toFixed(1)}% <tspan fill="#8b95a3" font-weight="normal">(${fmt(c.total)})</tspan></text>`;
  });

  svg.innerHTML = h;
}

// TABELA ANALÍTICA DE CONCENTRAÇÃO
function renderTable() {
  const tbody = document.getElementById('tblBody');
  const thead = document.getElementById('tblHead');
  const query = document.getElementById('tblSearch').value.toLowerCase().trim();

  let dictRef = D.parceiro;
  let colRef = C.parceiro;
  let titleCol = 'Parceiro Credenciado';

  if (currentTab === 'vendedor') { dictRef = D.vendedor; colRef = C.vendedor; titleCol = 'Vendedor / Agente'; }
  else if (currentTab === 'cidade') { dictRef = D.cidade; colRef = C.cidade; titleCol = 'Cidade / Município'; }
  else if (currentTab === 'canal') { dictRef = D.canal_grupo; colRef = C.canal; titleCol = 'Canal de Venda'; }

  thead.children[0].textContent = titleCol;

  const agg = dictRef.map((nome, idx) => ({ idx, nome, total: 0, ag60: 0, ag30: 0 }));

  for (let i = 0; i < N; i++) {
    if (!activeRows[i]) continue;
    const k = colRef[i];
    agg[k].total++;
    if (C.ag60[i]) agg[k].ag60++;
    if (C.ag30[i]) agg[k].ag30++;
  }

  let filtered = agg.filter(row => row.total > 0);
  if (query) {
    filtered = filtered.filter(row => row.nome.toLowerCase().includes(query));
  }

  // Ordenação
  filtered.forEach(r => {
    r.fpd60_pct = r.total > 0 ? (r.ag60 / r.total * 100) : 0;
    r.fpd30_pct = r.total > 0 ? (r.ag30 / r.total * 100) : 0;
    r.adimp_pct = r.total > 0 ? ((r.total - r.ag60) / r.total * 100) : 0;
  });

  filtered.sort((a,b) => (b.total - a.total)); // padrão volume desc
  filtered.sort((a,b) => (b[sortCol] - a[sortCol]) * (sortAsc ? -1 : 1));

  let h = '';
  filtered.slice(0, 150).forEach(r => {
    const rate60 = r.fpd60_pct;
    const barColor = rate60 > 25 ? '#c0392b' : (rate60 > 18 ? '#c98a15' : '#2f7d5d');
    h += `<tr>
      <td><b>${r.nome}</b></td>
      <td class="num">${fmt(r.total)}</td>
      <td class="num">${fmt(r.ag60)}</td>
      <td class="num">
        <span class="bar-cell"><span class="bar-fill" style="width:${Math.min(100, rate60 * 2.5)}%; background:${barColor};"></span></span>
        <b>${rate60.toFixed(2).replace('.',',')}%</b>
      </td>
      <td class="num">${fmt(r.ag30)}</td>
      <td class="num">${r.fpd30_pct.toFixed(2).replace('.',',')}%</td>
      <td class="num" style="color:var(--green); font-weight:600;">${r.adimp_pct.toFixed(2).replace('.',',')}%</td>
    </tr>`;
  });

  tbody.innerHTML = h;
}

function exportTableCsv() {
  const rows = [["Nome", "Instalacoes", "FPD_60_Volume", "Taxa_FPD_60_Pct", "FPD_30_Volume", "Taxa_FPD_30_Pct", "Adimplencia_Pct"]];
  const trs = document.querySelectorAll('#mainTable tbody tr');
  trs.forEach(tr => {
    const tds = [...tr.children].map(td => td.textContent.replace(/\\s+/g, ' ').trim());
    rows.push(tds);
  });
  const csvContent = "\\uFEFF" + rows.map(r => r.join(";")).join("\\n");
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `FPD_${currentTab}_Regional_Norte.csv`;
  a.click();
}

// MAPA CANVAS (WEB MERCATOR NATIVO)
const mapCv = document.getElementById('mapCv');
const mCtx = mapCv.getContext('2d');
let mapState = { z: 6, cx: -50.0, cy: -3.0, isDragging: false, lx: 0, ly: 0 };
let cityCentroids = [
  { nome: 'Manaus', lat: -3.1190, lon: -60.0217 },
  { nome: 'Belém', lat: -1.4558, lon: -48.4902 },
  { nome: 'São Luís', lat: -2.5391, lon: -44.2828 },
  { nome: 'Macapá', lat: 0.0389, lon: -51.0664 },
  { nome: 'Imperatriz', lat: -5.5266, lon: -47.4777 },
  { nome: 'Parauapebas', lat: -6.0678, lon: -49.9075 },
  { nome: 'Castanhal', lat: -1.2981, lon: -47.9248 },
  { nome: 'Marabá', lat: -5.3686, lon: -49.1174 },
  { nome: 'Ananindeua', lat: -1.3656, lon: -48.3744 },
  { nome: 'Santana', lat: -0.0583, lon: -51.1764 }
];

function setupMap() {
  function resizeCv() {
    mapCv.width = mapCv.parentElement.clientWidth;
    mapCv.height = 560;
    drawMap();
  }
  window.addEventListener('resize', resizeCv);
  resizeCv();

  mapCv.onmousedown = (e) => {
    if (isLassoActive) {
      const rect = mapCv.getBoundingClientRect();
      lassoPolygon = [[e.clientX - rect.left, e.clientY - rect.top]];
      return;
    }
    mapState.isDragging = true;
    mapState.lx = e.clientX;
    mapState.ly = e.clientY;
    mapCv.classList.add('drag');
  };

  window.onmousemove = (e) => {
    if (isLassoActive && lassoPolygon) {
      const rect = mapCv.getBoundingClientRect();
      lassoPolygon.push([e.clientX - rect.left, e.clientY - rect.top]);
      drawMap();
      return;
    }
    if (!mapState.isDragging) return;
    const dx = e.clientX - mapState.lx;
    const dy = e.clientY - mapState.ly;
    mapState.lx = e.clientX;
    mapState.ly = e.clientY;

    const ws = 256 * Math.pow(2, mapState.z);
    mapState.cx -= (dx / ws) * 360;
    mapState.cy += (dy / ws) * 180;
    drawMap();
  };

  window.onmouseup = () => {
    if (isLassoActive && lassoPolygon) {
      isLassoActive = false;
      mapCv.classList.remove('lasso');
      document.getElementById('btnLasso').classList.remove('on');
      // converter lasso para coordenadas lat/lon se desejar ou filtrar direto
      render();
      return;
    }
    mapState.isDragging = false;
    mapCv.classList.remove('drag');
  };

  mapCv.onwheel = (e) => {
    e.preventDefault();
    const zoomFactor = e.deltaY < 0 ? 1.2 : 0.8;
    mapState.z = Math.max(4, Math.min(12, mapState.z + (e.deltaY < 0 ? 0.3 : -0.3)));
    drawMap();
  };

  document.getElementById('btnZoomIn').onclick = () => { mapState.z = Math.min(12, mapState.z + 0.5); drawMap(); };
  document.getElementById('btnZoomOut').onclick = () => { mapState.z = Math.max(4, mapState.z - 0.5); drawMap(); };
  document.getElementById('btnResetMap').onclick = () => { mapState = { z: 6, cx: -50.0, cy: -3.0, isDragging: false, lx: 0, ly: 0 }; drawMap(); };
  document.getElementById('btnLasso').onclick = () => {
    isLassoActive = !isLassoActive;
    mapCv.classList.toggle('lasso', isLassoActive);
    document.getElementById('btnLasso').classList.toggle('on', isLassoActive);
  };
  document.getElementById('mapLayerSelect').onchange = drawMap;
}

function mercX(lon, ws) { return (lon + 180) / 360 * ws; }
function mercY(lat, ws) {
  const s = Math.sin(lat * Math.PI / 180);
  return (0.5 - Math.log((1 + s) / (1 - s)) / (4 * Math.PI)) * ws;
}

function drawMap() {
  const W = mapCv.width, H = mapCv.height;
  mCtx.clearRect(0, 0, W, H);

  // Fundo cartográfico neutro
  mCtx.fillStyle = '#e5eaed';
  mCtx.fillRect(0, 0, W, H);

  const ws = 256 * Math.pow(2, mapState.z);
  const midX = mercX(mapState.cx, ws);
  const midY = mercY(mapState.cy, ws);
  const offX = W / 2 - midX;
  const offY = H / 2 - midY;

  // Cidades Agrupadas
  const layer = document.getElementById('mapLayerSelect').value;
  const cityAgg = {};

  for (let i = 0; i < N; i++) {
    if (!activeRows[i]) continue;
    const cid = D.cidade[C.cidade[i]];
    if (!cityAgg[cid]) cityAgg[cid] = { total: 0, ag60: 0, ag30: 0, gx: C.gx[i], gy: C.gy[i] };
    cityAgg[cid].total++;
    if (C.ag60[i]) cityAgg[cid].ag60++;
    if (C.ag30[i]) cityAgg[cid].ag30++;
  }

  // Renderizar cidades e círculos proporcionais
  for (const cid in cityAgg) {
    const st = cityAgg[cid];
    const lat = BBOX[0] + (st.gy / 65534) * (BBOX[1] - BBOX[0]);
    const lon = BBOX[2] + (st.gx / 65534) * (BBOX[3] - BBOX[2]);

    const x = mercX(lon, ws) + offX;
    const y = mercY(lat, ws) + offY;

    if (x < -50 || x > W + 50 || y < -50 || y > H + 50) continue;

    const rate = st.ag60 / st.total;
    const r = Math.max(12, Math.min(48, Math.sqrt(st.total) * 1.4));

    // Círculo de fundo
    mCtx.beginPath();
    mCtx.arc(x, y, r, 0, Math.PI * 2);
    mCtx.fillStyle = rate > 0.25 ? 'rgba(192, 57, 43, 0.75)' : (rate > 0.18 ? 'rgba(201, 138, 21, 0.75)' : 'rgba(47, 125, 93, 0.75)');
    mCtx.fill();
    mCtx.lineWidth = 2;
    mCtx.strokeStyle = '#ffffff';
    mCtx.stroke();

    // Rótulo da Cidade e Taxa
    mCtx.fillStyle = '#ffffff';
    mCtx.font = 'bold 10.5px sans-serif';
    mCtx.textAlign = 'center';
    mCtx.fillText(cid, x, y - 2);

    mCtx.font = '9px sans-serif';
    mCtx.fillText(`${(rate * 100).toFixed(1)}%`, x, y + 10);
  }

  // Desenhar Polígono do Laço se ativo
  if (lassoPolygon && lassoPolygon.length > 1) {
    mCtx.beginPath();
    mCtx.moveTo(lassoPolygon[0][0], lassoPolygon[0][1]);
    for (let i = 1; i < lassoPolygon.length; i++) {
      mCtx.lineTo(lassoPolygon[i][0], lassoPolygon[i][1]);
    }
    mCtx.strokeStyle = '#c0392b';
    mCtx.lineWidth = 2;
    mCtx.fillStyle = 'rgba(192,57,43,0.15)';
    mCtx.fill();
    mCtx.stroke();
  }

  // Renderizar Lista Lateral de Praças
  renderMapSidebar(cityAgg);
}

function renderMapSidebar(cityAgg) {
  const box = document.getElementById('mapCitiesList');
  const sorted = Object.keys(cityAgg).map(k => ({ nome: k, ...cityAgg[k] })).sort((a,b) => b.total - a.total);

  let h = '';
  sorted.forEach(c => {
    const rate = (c.ag60 / c.total * 100).toFixed(1);
    const badgeColor = rate > 25 ? '#c0392b' : (rate > 18 ? '#c98a15' : '#2f7d5d');
    h += `<div class="map-city-row" onclick="filterByCityName('${c.nome}')">
      <div>
        <b style="font-size:11.5px;">${c.nome}</b>
        <div style="font-size:10px; color:var(--ink3);">${fmt(c.total)} inst</div>
      </div>
      <div style="text-align:right;">
        <span style="background:${badgeColor}; color:#fff; padding:2px 6px; border-radius:3px; font-weight:700; font-size:10.5px;">${rate}%</span>
      </div>
    </div>`;
  });
  box.innerHTML = h;
}

window.filterByCityName = function(cityName) {
  const idx = D.cidade.indexOf(cityName);
  if (idx !== -1) {
    document.getElementById('fltCidade').value = idx;
    readFilters();
    render();
  }
};

// INICIALIZAR QUANDO CARREGAR
window.addEventListener('DOMContentLoaded', initData);

</script>
</body>
</html>
"""

# 1. Salvar na raiz
with open('Painel_FPD_Regional_Norte.html', 'w', encoding='utf-8') as f:
    f.write(html_template)
print("Gerado Painel_FPD_Regional_Norte.html na raiz com sucesso!")

# 2. Criar diretório public/fpd se não existir
os.makedirs('public/fpd', exist_ok=True)
with open('public/fpd/index.html', 'w', encoding='utf-8') as f:
    f.write(html_template)
print("Gerado public/fpd/index.html com sucesso!")
