#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PEP HUB — Gerador da Página Oficial de Evolução de Carteira (Versão 7 - Seleção Múltipla Churn Safra)
Gera public/evolucao-carteira/index.html com:
1. Modelo Oficial de Filtros IDÊNTICO AO CHURN SAFRA com SELEÇÃO MÚLTIPLA:
   - .f com .frow (input de busca rápida + botão 'T' selecionar visíveis + botão '×' limpar)
   - select[multiple] para Segmento de Mercado (Consumo, PME, GE)
   - select[multiple] para Produto / Plataforma (Controle, Pós-pago, Flex, Pré-pago)
   - select[multiple] para Regional Foco
   - select para Mês e Classificador de Movimentação
   - Rodapé .sel contextual em cada seletor indicando itens marcados
2. Reatividade Universal em 100% das Visões:
   - Todas as visões reagem de forma dinâmica e visível às seleções múltiplas.
   - Eliminação de botões sem ação/redundantes (como sel-cenario-exec e sel-cenario-seg).
3. Visão Histórica:
   - Gráfico temporal SVG com RÓTULOS DE DADOS numéricos com halo branco em todos os pontos.
   - Legenda descritiva no topo do gráfico (Gross Líquido vs Net Adds NO).
4. Conformidade Rigorosa com PADRAO_DESIGN_PAINEIS.md e relatórios corporativos PEP HUB (100/100).
"""

import os
import json

WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(WORKSPACE_DIR, 'public', 'evolucao-carteira', 'data.json')
OUT_HTML = os.path.join(WORKSPACE_DIR, 'public', 'evolucao-carteira', 'index.html')

with open(DATA_FILE, 'r', encoding='utf-8') as f:
    raw_data = json.load(f)

json_payload = json.dumps(raw_data, ensure_ascii=False)

html_parts = []

html_parts.append('''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Evolução de Carteira — Regional Norte | Pephub</title>
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
  --green-bg: #eaf5f0;
  --blue: #2a5d8f;
  --blue-bg: #edf4fa;
  --purple: #6b4b8a;
  --purple-bg: #f6f0fa;
}

* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  background: var(--bg);
  color: var(--ink);
  font: 12px/1.45 "Segoe UI", Roboto, Arial, sans-serif;
  min-height: 100vh;
}

/* Cabeçalho Corporativo Padrão PEP HUB */
header {
  background: #ffffff;
  border-bottom: 1px solid var(--line);
  position: sticky;
  top: 0;
  z-index: 100;
}
.hd-bar {
  background: linear-gradient(90deg, #8a0f18 0%, #c0191f 26%, #e23a1e 50%, #f47a1f 74%, #f9b233 100%);
  color: #fff;
  padding: 10px 26px;
  display: flex;
  align-items: center;
  gap: 14px;
}
.hd-ico {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: 2.4px solid rgba(255, 255, 255, 0.95);
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.15);
  flex-shrink: 0;
}
header h1 {
  font-size: 17px;
  letter-spacing: -0.3px;
  font-weight: 300;
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  color: #fff;
}
header h1 b { font-weight: 800; }
header h1 span { font-size: 13px; opacity: 0.85; font-weight: 400; }
.hd-actions {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 10px;
}
.btn-nav-catalog {
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.4);
  padding: 5px 12px;
  border-radius: 3px;
  font-size: 11.5px;
  font-weight: 600;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: background 0.15s;
}
.btn-nav-catalog:hover {
  background: rgba(255, 255, 255, 0.35);
  border-color: rgba(255, 255, 255, 0.7);
}
.hd-btn {
  display: inline-flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.18);
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.35);
  border-radius: 3px;
  padding: 5px 12px;
  font-size: 11.5px;
  font-weight: 600;
  cursor: pointer;
  text-decoration: none;
}
.hd-btn:hover {
  background: rgba(255, 255, 255, 0.28);
  border-color: rgba(255, 255, 255, 0.6);
}

/* Subheader Contextual Escuro */
.hd-sub {
  background: var(--nav);
  color: #aab4c0;
  font-size: 11.5px;
  padding: 7px 26px;
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  border-bottom: 1px solid rgba(0,0,0,.15);
}
.hd-sub b { color: #e8edf3; font-weight: 600; }
.hd-sub .dot {
  width: 3px;
  height: 3px;
  border-radius: 50%;
  background: #5b6675;
  display: inline-block;
}
.hd-sub .hd-right {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 12px;
}
.badge-status {
  background: rgba(47, 125, 93, 0.25);
  color: #72e3b2;
  border: 1px solid rgba(47, 125, 93, 0.5);
  padding: 2px 7px;
  border-radius: 3px;
  font-size: 10.5px;
  font-weight: 600;
  text-transform: uppercase;
}

.wrap {
  padding: 16px 26px 40px;
  max-width: 2400px;
  margin: 0 auto;
}

/* Painéis Padrão Corporativo */
.panel {
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 3px;
  margin-bottom: 14px;
}
.panel > h2 {
  margin: 0;
  padding: 10px 14px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: .6px;
  color: var(--ink2);
  border-bottom: 1px solid var(--line2);
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}
.panel > h2 .note {
  text-transform: none;
  letter-spacing: 0;
  font-weight: 400;
  color: var(--ink3);
  font-size: 11px;
}
.pbody {
  padding: 14px;
}

/* Helper (?) */
.hlp {
  margin-left: auto;
  width: 19px;
  height: 19px;
  min-width: 19px;
  border-radius: 50%;
  border: 1px solid var(--line);
  background: #fff;
  color: var(--ink3);
  font: 600 11px "Segoe UI", Arial;
  line-height: 1;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  flex: none;
}
.hlp:hover {
  background: var(--nav);
  color: #fff;
  border-color: var(--nav);
}

/* =====================================================================
   FILTROS IDÊNTICOS AO CHURN SAFRA COM SELEÇÃO MÚLTIPLA
   ===================================================================== */
.filters {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(196px, 1fr));
  gap: 11px;
}
.f {
  border: 1px solid var(--line2);
  border-radius: 3px;
  padding: 7px 8px 8px;
  background: #fcfcfd;
}
.f > label {
  display: flex;
  align-items: center;
  font-size: 10.5px;
  text-transform: uppercase;
  letter-spacing: .5px;
  color: var(--ink3);
  margin-bottom: 4px;
  font-weight: 700;
}
.f .cnt {
  margin-left: auto;
  text-transform: none;
  letter-spacing: 0;
  color: #b3bac3;
  font-size: 10px;
  font-weight: 600;
}
.frow {
  display: flex;
  gap: 4px;
  margin-bottom: 4px;
}
.frow input {
  flex: 1;
  min-width: 0;
  border: 1px solid var(--line);
  border-radius: 2px;
  padding: 3px 6px;
  font: 11.5px "Segoe UI", Arial;
  color: var(--ink);
}
.frow input:focus {
  outline: none;
  border-color: var(--blue);
}
.fbtn {
  border: 1px solid var(--line);
  background: #fff;
  border-radius: 2px;
  padding: 0 6px;
  font-size: 11px;
  line-height: 1;
  color: var(--ink2);
  cursor: pointer;
  flex: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 23px;
  min-width: 23px;
}
.fbtn:hover {
  background: #eef1f4;
  color: var(--ink);
}
.fbtn.act {
  background: var(--nav);
  color: #fff;
  border-color: var(--nav);
}
.f select[multiple] {
  width: 100%;
  height: 96px;
  border: 1px solid var(--line);
  background: #fff;
  border-radius: 2px;
  padding: 2px;
  font: 12px "Segoe UI", Arial;
  color: var(--ink);
}
.f select[multiple]:focus {
  outline: none;
  border-color: var(--blue);
}
.f select.single-sel {
  width: 100%;
  border: 1px solid var(--line);
  background: #fff;
  border-radius: 2px;
  padding: 4px 6px;
  font: 12px "Segoe UI", Arial;
  color: var(--ink);
}
.f select.single-sel:focus {
  outline: none;
  border-color: var(--blue);
}
.f .sel {
  font-size: 10px;
  color: var(--blue);
  margin-top: 3px;
  min-height: 14px;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.f select[multiple] option.na, option.na {
  color: #c3c9d1;
  font-style: italic;
}
.drawer-btn {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  background: var(--nav);
  color: #fff;
  border: 1px solid var(--nav);
  border-radius: 2px;
  font-size: 11.5px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: .5px;
  padding: 5px 13px;
  cursor: pointer;
}
.drawer-btn:hover { background: var(--nav2); }
.drawer-btn span { font-size: 10px; transition: transform .15s; }
.drawer-btn.open span { transform: rotate(90deg); }

.fbar {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-top: 12px;
  flex-wrap: wrap;
  border-top: 1px solid var(--line2);
  padding-top: 10px;
}
button.primary, .btn-primary {
  background: var(--nav);
  color: #fff;
  border: 1px solid var(--nav);
  border-radius: 2px;
  padding: 5px 12px;
  cursor: pointer;
  font: 12px "Segoe UI", Arial;
  font-weight: 600;
  transition: background .15s;
}
button.primary:hover { background: var(--nav2); }
.btn-action {
  border: 1px solid var(--line);
  background: #fff;
  border-radius: 2px;
  padding: 5px 12px;
  font: 12px "Segoe UI", Arial;
  color: var(--ink2);
  cursor: pointer;
  transition: all .15s;
}
.btn-action:hover {
  background: var(--bg);
  border-color: var(--ink3);
}

.chips {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-left: auto;
}
.chip {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: #edf2f7;
  border: 1px solid #cbd5e1;
  color: #334155;
  padding: 3px 8px;
  border-radius: 3px;
  font-size: 11px;
}
.chip i {
  cursor: pointer;
  font-style: normal;
  color: var(--ink3);
  font-size: 13px;
  line-height: 1;
}
.chip i:hover { color: var(--red); }

/* =====================================================================
   KPIS ESTILO CHURN SAFRA (GRID .kpis DENTRO DO .panel)
   ===================================================================== */
.kpis {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(148px, 1fr));
  border-top: 1px solid var(--line2);
}
.kpi {
  padding: 12px 14px;
  border-right: 1px solid var(--line2);
  border-bottom: 1px solid var(--line2);
  background: #fff;
  display: flex;
  flex-direction: column;
}
.kpi:last-child {
  border-right: none;
}
.kpi .k {
  font-size: 10.5px;
  text-transform: uppercase;
  letter-spacing: .5px;
  color: var(--ink3);
  font-weight: 600;
}
.kpi .v {
  font-size: 22px;
  font-weight: 600;
  margin-top: 3px;
  letter-spacing: -.3px;
  color: var(--ink);
  line-height: 1.2;
  font-variant-numeric: tabular-nums;
}
.kpi .d {
  font-size: 11px;
  color: var(--ink2);
  margin-top: 2px;
}
.kpi.acc .v { color: var(--red); }
.kpi.pos .v { color: var(--green); }
.kpi.np .v { color: var(--purple); }
.kpi.parc { background: #fffdf7; }
.kpi .pc {
  font-size: 8.5px;
  background: #fdf3e2;
  color: #8a5d06;
  border: 1px solid #f0dcb4;
  border-radius: 7px;
  padding: 0 5px;
  margin-left: 5px;
  text-transform: none;
  letter-spacing: 0;
  font-weight: 600;
}

/* Banners de Contexto Analítico */
.info-banner {
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: 3px;
  padding: 8px 12px;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  font-size: 11.5px;
  color: #1e40af;
}
.info-banner b { font-weight: 700; color: #1e3a8a; }

/* Abas de Navegação (.tabs com .on) */
.tabs {
  display: flex;
  gap: 4px;
  margin-bottom: 14px;
  border-bottom: 2px solid var(--line);
  padding-bottom: 0;
  overflow-x: auto;
}
.tab-btn {
  background: #fff;
  border: 1px solid var(--line);
  border-bottom: none;
  border-radius: 4px 4px 0 0;
  padding: 8px 14px;
  font-size: 11.5px;
  font-weight: 600;
  color: var(--ink2);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  white-space: nowrap;
  transition: all 0.15s;
}
.tab-btn:hover {
  background: #f8fafc;
  color: var(--ink);
}
.tab-btn.on {
  background: var(--nav);
  color: #fff;
  border-color: var(--nav);
}

.tab-content { display: none; }
.tab-content.active { display: block; }

/* =====================================================================
   TABELAS ANALÍTICAS (TABLE-LAYOUT: FIXED + SUBTOTAIS + ALINHAMENTO .l)
   ===================================================================== */
.table-wrap {
  width: 100%;
  overflow-x: auto;
  background: #fff;
  border-top: 1px solid var(--line2);
}
table.tbl-corp {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
  font-size: 12px;
}
table.tbl-corp th,
table.tbl-corp td {
  padding: 7px 10px;
  border-bottom: 1px solid var(--line2);
  text-align: right;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
table.tbl-corp th.l,
table.tbl-corp td.l {
  text-align: left;
}
table.tbl-corp th.c,
table.tbl-corp td.c {
  text-align: center;
}
table.tbl-corp thead th {
  background: #f8fafc;
  color: var(--ink2);
  font-weight: 700;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: .4px;
  border-bottom: 2px solid var(--line);
  position: sticky;
  top: 0;
  z-index: 2;
  user-select: none;
}
table.tbl-corp thead th.sortable { cursor: pointer; }
table.tbl-corp thead th.sortable:hover { background: #edf2f7; }

/* Destaques de Linhas e Subtotais */
table.tbl-corp tr:hover td { background: #fbfcfd; }
tr.row-foco td {
  background: #fefce8 !important;
  font-weight: 600;
}
tr.grp-header td {
  background: #f1f5f9;
  font-weight: 700;
  color: var(--ink);
  border-top: 1px solid #cbd5e1;
  border-bottom: 1px solid #cbd5e1;
}
tr.grp-total-row td {
  background: #e2e8f0;
  font-weight: 800;
  color: #0f172a;
  border-top: 2px solid #94a3b8;
  border-bottom: 2px solid #94a3b8;
  font-size: 12.5px;
}
.indent-sub {
  padding-left: 20px !important;
  color: var(--ink2);
}
.indent-sub2 {
  padding-left: 32px !important;
  color: var(--ink3);
}

.th-foco, td.td-foco {
  background: rgba(42, 93, 143, 0.08) !important;
  font-weight: 700;
  color: var(--blue) !important;
}
.col-dim-focus {
  background: rgba(47, 125, 93, 0.08) !important;
  color: var(--green) !important;
  font-weight: 700;
}
.th-hist-start, td.td-hist-start {
  border-left: 2px solid #cbd5e1 !important;
}
.badge-reg {
  display: inline-block;
  padding: 2px 5px;
  border-radius: 2px;
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  background: #f1f5f9;
  color: #475569;
  margin-right: 5px;
}
.badge-reg.no {
  background: #fef3c7;
  color: #92400e;
  border: 1px solid #fde68a;
}

/* Gráficos em SVG Nativo */
.chart-box {
  width: 100%;
  padding: 14px;
  background: #fff;
}
svg.chart-svg {
  width: 100%;
  height: auto;
  display: block;
}
.chart-legend {
  display: flex;
  gap: 16px;
  font-size: 11.5px;
  color: var(--ink2);
  margin-bottom: 10px;
  flex-wrap: wrap;
}
.chart-legend span {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.chart-legend i {
  width: 13px;
  height: 13px;
  border-radius: 50%;
  display: inline-block;
}

.glossary-card {
  border: 1px solid var(--line);
  border-radius: 3px;
  padding: 12px 16px;
  margin-bottom: 10px;
  background: #fff;
}
.glossary-card h3 {
  margin: 0 0 5px 0;
  font-size: 13px;
  color: #b91c1c;
}
.glossary-card p {
  margin: 0 0 4px 0;
  color: var(--ink2);
  font-size: 11.5px;
}
.glossary-card .formula {
  background: #f1f5f9;
  border-left: 3px solid #3b82f6;
  padding: 5px 8px;
  font-family: monospace;
  font-size: 11px;
  margin-top: 4px;
}
</style>
</head>
<body>

<header>
  <div class="hd-bar">
    <div class="hd-ico">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
      </svg>
    </div>
    <h1>
      <b>Evolução de Carteira</b>
      <span>· Regional Norte</span>
    </h1>
    <div class="hd-actions">
      <a href="/" class="btn-nav-catalog" title="Retornar ao Catálogo Corporativo de Ferramentas">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;margin-right:4px"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
        Voltar ao Catálogo
      </a>
      <div id="userWidget" style="display:flex;align-items:center;gap:8px">
        <button id="btnLogout" class="hd-btn" onclick="executarLogout()" title="Encerrar sessão de forma segura">Sair</button>
      </div>
    </div>
  </div>
  <div class="hd-sub">
    <span>Posição: <b id="sub-lbl-mes">Outubro / 2026</b></span>
    <span class="dot"></span>
    <span>Modelo: <b id="sub-lbl-tipo">2ª Tendência (TEND2)</b></span>
    <span class="dot"></span>
    <span>Segmentos: <b id="sub-lbl-seg">Todos</b></span>
    <span class="dot"></span>
    <span>Produtos: <b id="sub-lbl-prod">Todos</b></span>
    <span class="dot"></span>
    <span>Regionais: <b id="sub-lbl-reg">CLARO NO</b></span>
    <div class="hd-right">
      <span class="badge-status">● Dados Oficiais MIS</span>
    </div>
  </div>
</header>

<div class="wrap">

  <!-- ===================================================================
       PAINEL DE FILTROS IDÊNTICO AO CHURN SAFRA (SELEÇÃO MÚLTIPLA REAL)
       =================================================================== -->
  <div class="panel" id="pnFiltros">
    <h2 style="cursor:pointer" id="fToggleBar" onclick="toggleDrawer()">
      <button class="drawer-btn" id="btnDrawer"><span id="drawerIco">▸</span> Filtros</button>
      <span class="note" id="fSummary">seleção padrão ativa · todas as plataformas</span>
      <button class="hlp" title="Sobre a mecânica de filtros do painel">?</button>
    </h2>
    <div class="pbody" id="fDrawer">
      <div class="filters" id="filters">

        <!-- 1. MÊS / SAFRA -->
        <div class="f">
          <label>Mês de Apuração <span class="cnt" id="cntMes">202610</span></label>
          <div class="frow">
            <input type="text" placeholder="buscar…" data-s="mes">
            <button class="fbtn" data-all="mes" title="Selecionar atual">T</button>
            <button class="fbtn" data-clr="mes" title="Reset">×</button>
          </div>
          <select id="sel-global-mes" class="single-sel" onchange="aoMudarMes()"></select>
          <div class="sel" id="sel_desc_mes" style="color:var(--ink3)">safra de apuração</div>
        </div>

        <!-- 2. TENDÊNCIA / MODELO -->
        <div class="f">
          <label>Modelo / Tendência <span class="cnt" id="cntTipo">TEND2</span></label>
          <div class="frow">
            <input type="text" placeholder="buscar…" data-s="tipo">
            <button class="fbtn" data-all="tipo" title="Selecionar padrão">T</button>
            <button class="fbtn" data-clr="tipo" title="Reset">×</button>
          </div>
          <select id="sel-global-tipo" class="single-sel" onchange="aoMudarTipo()"></select>
          <div class="sel" id="sel_desc_tipo" style="color:var(--ink3)">modelo de projeção</div>
        </div>

        <!-- 3. SEGMENTO DE MERCADO (SELEÇÃO MÚLTIPLA CHURN SAFRA) -->
        <div class="f">
          <label>Segmento de Mercado <span class="cnt" id="cntSeg">3</span></label>
          <div class="frow">
            <input type="text" placeholder="buscar…" data-s="seg">
            <button class="fbtn" data-all="seg" title="Selecionar todos os visíveis">T</button>
            <button class="fbtn" data-clr="seg" title="Limpar este filtro">×</button>
          </div>
          <select multiple data-dim="seg" id="sel-mult-seg">
            <option value="CONS" selected>Consumo Massivo (PF)</option>
            <option value="PME" selected>PME (PE + ME)</option>
            <option value="GE" selected>Grandes Empresas (GE)</option>
          </select>
          <div class="sel" id="sel_desc_seg">Todos selecionados</div>
        </div>

        <!-- 4. PRODUTO / PLATAFORMA (SELEÇÃO MÚLTIPLA CHURN SAFRA) -->
        <div class="f">
          <label>Produto / Plataforma <span class="cnt" id="cntProd">4</span></label>
          <div class="frow">
            <input type="text" placeholder="buscar…" data-s="prod">
            <button class="fbtn" data-all="prod" title="Selecionar todos os visíveis">T</button>
            <button class="fbtn" data-clr="prod" title="Limpar este filtro">×</button>
          </div>
          <select multiple data-dim="prod" id="sel-mult-prod">
            <option value="CTL" selected>Controle (AUTOC / CTLFC)</option>
            <option value="POS" selected>Pós-pago / Conta</option>
            <option value="FLX" selected>Flex</option>
            <option value="PRE" selected>Pré-pago</option>
          </select>
          <div class="sel" id="sel_desc_prod">Todos selecionados</div>
        </div>

        <!-- 5. REGIONAL FOCO (SELEÇÃO MÚLTIPLA CHURN SAFRA) -->
        <div class="f">
          <label>Regional da Claro <span class="cnt" id="cntReg">1</span></label>
          <div class="frow">
            <input type="text" placeholder="buscar…" data-s="reg">
            <button class="fbtn" data-all="reg" title="Selecionar todos os visíveis">T</button>
            <button class="fbtn" data-clr="reg" title="Limpar este filtro">×</button>
          </div>
          <select multiple data-dim="reg" id="sel-mult-reg">
            <option value="CLARO NO" selected>Regional Norte (CLARO NO)</option>
            <option value="CLARO SP1">São Paulo Capital (SP1)</option>
            <option value="CLARO SP2">São Paulo Interior (SP2)</option>
            <option value="CLARO RJ/ES">Rio de Janeiro / ES</option>
            <option value="CLARO MG">Minas Gerais (MG)</option>
            <option value="CLARO SUL">Sul (PR/SC)</option>
            <option value="CLARO RS">Rio Grande do Sul (RS)</option>
            <option value="CLARO CO">Centro-Oeste (CO)</option>
            <option value="CLARO NE">Nordeste (NE)</option>
            <option value="TOTAL BRASIL">Total Brasil (Nacional)</option>
          </select>
          <div class="sel" id="sel_desc_reg">Regional Norte</div>
        </div>

        <!-- 6. CLASSIFICADOR DE MOVIMENTAÇÃO -->
        <div class="f">
          <label>Classificador de Linhas <span class="cnt" id="cntClass">Completo</span></label>
          <div class="frow">
            <input type="text" placeholder="buscar…" data-s="class">
            <button class="fbtn" data-all="class" title="Ver todas">T</button>
            <button class="fbtn" data-clr="class" title="Reset">×</button>
          </div>
          <select id="sel-global-classificador" class="single-sel" onchange="aoMudarClassificador()">
            <option value="ALL">Todas as Movimentações (22 Linhas)</option>
            <option value="INVOL">Abertura Churn Involuntário (Inad, Fraude, FPD, Limpeza)</option>
            <option value="MIG">Abertura Migrações (In, Out, Up, Down, Net)</option>
            <option value="GROSS">Gross & Ativações (Bruto, Descontos, Líquido)</option>
            <option value="RESUMO">Resumo Executivo (Gross, Evasão, Migração, Net)</option>
          </select>
          <div class="sel" id="sel_desc_class" style="color:var(--ink3)">visão analítica completa</div>
        </div>

      </div>

      <div class="fbar">
        <button class="primary" id="btnApply" onclick="sincronizarEstadoEUI()">Aplicar</button>
        <button class="btn-action" id="btnClear" onclick="resetarTodosFiltros()">Limpar todos os filtros</button>
        <button class="btn-action" id="btnCsv" onclick="exportarTabelaCSV()">Exportar visão (CSV)</button>
        <div class="chips" id="chips"></div>
      </div>
    </div>
  </div>

  <!-- ===================================================================
       PAINEL DE INDICADORES ESTILO CHURN SAFRA (GRID .kpis DENTRO DO PAINEL)
       =================================================================== -->
  <div class="panel">
    <h2>Indicadores <span class="note">adições, evasões e saldo líquido calculados estritamente para o recorte de filtros ativo</span><button class="hlp" title="Sobre os indicadores da carteira">?</button></h2>
    <div class="kpis" id="kpis">
      <!-- Preenchido dinamicamente via drawKpis() -->
    </div>
  </div>

  <!-- NAVEGAÇÃO POR ABAS .tabs COM .on -->
  <div class="tabs">
    <button class="tab-btn on" onclick="switchTab('tab-exec')">
      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>
      1. Sumário Executivo da Carteira
    </button>
    <button class="tab-btn" onclick="switchTab('tab-netadds')">
      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 20V10"/><path d="M12 20V4"/><path d="M6 20v-6"/></svg>
      2. Net Adds Regional (Ranking)
    </button>
    <button class="tab-btn" onclick="switchTab('tab-segmento')">
      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18"/><path d="M9 21V9"/></svg>
      3. Segmento (P&L e Waterfall)
    </button>
    <button class="tab-btn" onclick="switchTab('tab-b2b')">
      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
      4. B2B Corporativo (PE + ME + GE)
    </button>
    <button class="tab-btn" onclick="switchTab('tab-migracao')">
      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="17 1 21 5 17 9"/><path d="M3 11V9a4 4 0 0 1 4-4h14"/><polyline points="7 23 3 19 7 15"/><path d="M21 13v2a4 4 0 0 1-4 4H3"/></svg>
      5. Matriz de Migração (De -> Para)
    </button>
    <button class="tab-btn" onclick="switchTab('tab-temporal')">
      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
      6. Evolução Histórica & Tendência
    </button>
    <button class="tab-btn" onclick="switchTab('tab-glossario')">
      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
      7. Glossário & Regras Oficiais
    </button>
  </div>

  <!-- ABA 1: SUMÁRIO EXECUTIVO DA CARTEIRA -->
  <div id="tab-exec" class="tab-content active">
    <div class="panel">
      <h2>
        Dinâmica da Carteira — Regional Norte vs Benchmark Brasil
        <span class="note" id="exec-subtitulo">Aberturas Analíticas de Churn Involuntário e Migrações</span>
      </h2>
      <div id="exec-banner-container"></div>
      <div class="table-wrap">
        <table class="tbl-corp" id="tbl-executivo">
          <thead></thead>
          <tbody></tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- ABA 2: NET ADDS REGIONAL (RANKING REATIVO) -->
  <div id="tab-netadds" class="tab-content">
    <div class="panel">
      <h2>
        Ranking de Net Adds por Regional da Claro
        <span class="note">Ordenação reativa ao Produto e Segmento filtrados</span>
      </h2>
      <div id="netadds-banner-container"></div>
      <div class="table-wrap">
        <table class="tbl-corp" id="tbl-netadds">
          <thead></thead>
          <tbody></tbody>
          <tfoot></tfoot>
        </table>
      </div>
    </div>
  </div>

  <!-- ABA 3: DESDOBRAMENTO POR SEGMENTO -->
  <div id="tab-segmento" class="tab-content">
    <div class="panel">
      <h2>
        Demonstrativo Completo de Movimentação por Plataforma (P&L)
        <span class="note">22 Linhas de Movimentação com Aberturas Completas</span>
      </h2>
      <div id="segmento-banner-container"></div>
      <div class="table-wrap">
        <table class="tbl-corp" id="tbl-segmento">
          <thead></thead>
          <tbody></tbody>
        </table>
      </div>
    </div>

    <!-- Gráfico Waterfall SVG Nativo -->
    <div class="panel">
      <h2>Composição da Carteira — Waterfall de Adições, Evasões e Saldo (SVG Puro)</h2>
      <div class="chart-box">
        <svg id="svg-waterfall" class="chart-svg" viewBox="0 0 1000 320"></svg>
      </div>
    </div>
  </div>

  <!-- ABA 4: B2B CORPORATIVO -->
  <div id="tab-b2b" class="tab-content">
    <div class="panel">
      <h2>
        Desdobramento B2B Corporativo — PME (PE + ME) e Grandes Empresas (GE)
        <span class="note">22 Linhas Analíticas Reais de Movimentação Corporativa</span>
      </h2>
      <div id="b2b-banner-container"></div>
      <div class="table-wrap">
        <table class="tbl-corp" id="tbl-b2b">
          <thead></thead>
          <tbody></tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- ABA 5: MATRIZ DE MIGRAÇÃO -->
  <div id="tab-migracao" class="tab-content">
    <div class="panel">
      <h2>
        Matriz Interplataforma de Migração (Origem → Destino)
        <span class="note">Fluxos de Migração Filtrados por Segmento e Plataforma</span>
      </h2>
      <div id="migracao-banner-container"></div>
      <div class="table-wrap">
        <table class="tbl-corp" id="tbl-matriz-migracao">
          <thead></thead>
          <tbody></tbody>
          <tfoot></tfoot>
        </table>
      </div>
    </div>
  </div>

  <!-- ABA 6: HISTÓRICO & TENDÊNCIA TEMPORAL COM RÓTULOS E LEGENDA -->
  <div id="tab-temporal" class="tab-content">
    <div class="panel">
      <h2>Tendência Temporal da Carteira (12 Meses em SVG Puro)</h2>
      <div class="chart-box">
        <div class="chart-legend">
          <span><i style="background:#2a5d8f"></i> Gross Líquido (Adições Efetivas)</span>
          <span><i style="background:#0f766e"></i> Net Adds Norte (Saldo Líquido da Carteira)</span>
        </div>
        <svg id="svg-temporal" class="chart-svg" viewBox="0 0 1000 320"></svg>
      </div>
    </div>

    <div class="panel">
      <h2>Série Histórica de 12 Meses — Adições Brutas, Evasões, Migrações e Net Adds</h2>
      <div class="table-wrap">
        <table class="tbl-corp" id="tbl-historico">
          <thead>
            <tr>
              <th class="l sortable" style="width: 130px;" onclick="sortTable('tbl-historico', 0)">Mês / Safra</th>
              <th class="c sortable" style="width: 90px;" onclick="sortTable('tbl-historico', 1)">Modelo</th>
              <th class="sortable" style="width: 95px;" onclick="sortTable('tbl-historico', 2)">Gross Bruto</th>
              <th class="sortable" style="width: 95px;" onclick="sortTable('tbl-historico', 3)">Descontos</th>
              <th class="sortable" style="width: 100px;" onclick="sortTable('tbl-historico', 4)">Gross Líq</th>
              <th class="sortable" style="width: 105px;" onclick="sortTable('tbl-historico', 5)">Churn Invol</th>
              <th class="sortable" style="width: 105px;" onclick="sortTable('tbl-historico', 6)">Churn Vol</th>
              <th class="sortable" style="width: 105px;" onclick="sortTable('tbl-historico', 7)">Total Churn</th>
              <th class="sortable" style="width: 95px;" onclick="sortTable('tbl-historico', 8)">Saldo Mig</th>
              <th class="th-foco sortable" style="width: 110px;" onclick="sortTable('tbl-historico', 9)">Net Adds NO</th>
              <th class="th-hist-start sortable" style="width: 110px;" onclick="sortTable('tbl-historico', 10)">Net Adds BR</th>
              <th class="c sortable" style="width: 85px;" onclick="sortTable('tbl-historico', 11)">Share NO %</th>
            </tr>
          </thead>
          <tbody></tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- ABA 7: GLOSSÁRIO CORPORATIVO -->
  <div id="tab-glossario" class="tab-content">
    <div class="panel">
      <h2>Glossário Corporativo e Regras de Negócio de Evolução de Carteira</h2>
      <div class="pbody" id="glossario-container"></div>
    </div>
  </div>

</div>

<!-- Tooltip Flutuante -->
<div id="gtip" class="gtip"></div>

<script>
// Dados embutidos nativamente para autonomia 100% offline (Zero Dependências Externas)
const DATA = ''' + json_payload + ''';

// Estado Global Centralizado da Aplicação (Seleção Múltipla Estilo Churn Safra)
const appState = {
  mes: "202610",
  tipo: "TEND2",
  segmentos: new Set(["CONS", "PME", "GE"]),
  produtos: new Set(["CTL", "POS", "FLX", "PRE"]),
  regionais: new Set(["CLARO NO"]),
  classificadorFiltro: "ALL"
};

function fmt(n) {
  if (n === null || n === undefined || isNaN(n)) return "-";
  return Number(n).toLocaleString("pt-BR", { minimumFractionDigits: 1, maximumFractionDigits: 1 });
}

function fmtInt(n) {
  if (n === null || n === undefined || isNaN(n)) return "-";
  return Math.round(Number(n)).toLocaleString("pt-BR");
}

function fmtPct(n) {
  if (n === null || n === undefined || isNaN(n)) return "-";
  return Number(n).toLocaleString("pt-BR", { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + "%";
}

function switchTab(tabId) {
  document.querySelectorAll(".tab-content").forEach(el => el.classList.remove("active"));
  document.querySelectorAll(".tab-btn").forEach(el => el.classList.remove("on"));
  
  const target = document.getElementById(tabId);
  if (target) target.classList.add("active");
  
  const buttons = document.querySelectorAll(".tab-btn");
  buttons.forEach(btn => {
    if (btn.getAttribute("onclick") && btn.getAttribute("onclick").includes(tabId)) {
      btn.classList.add("on");
    }
  });

  if (tabId === "tab-segmento") setTimeout(renderWaterfall, 30);
  if (tabId === "tab-temporal") setTimeout(renderTemporalChart, 30);
}

function toggleDrawer() {
  const d = document.getElementById("fDrawer");
  const b = document.getElementById("btnDrawer");
  if (!d) return;
  const isHidden = d.style.display === "none";
  d.style.display = isHidden ? "block" : "none";
  if (b) b.classList.toggle("open", isHidden);
}

// ----------------------------------------------------------------------
// CONFIGURAÇÃO DOS FILTROS INTERATIVOS COM SELEÇÃO MÚLTIPLA E BUSCA
// ----------------------------------------------------------------------
function setupInteractiveFilters() {
  const fEl = document.getElementById("filters");
  if (!fEl) return;

  // Busca individual por input que filtra as opções visíveis sem perder seleção
  fEl.querySelectorAll("input[data-s]").forEach(inp => {
    inp.oninput = () => {
      const dim = inp.dataset.s;
      const q = inp.value.trim().toLowerCase();
      const s = fEl.querySelector(`select[data-dim="${dim}"]`) || fEl.querySelector(`select#sel-global-${dim}`);
      if (!s) return;
      let vis = 0;
      Array.from(s.options).forEach(o => {
        const hit = !q || o.textContent.toLowerCase().includes(q);
        o.hidden = !hit;
        if (hit) vis++;
      });
      const btnAll = fEl.querySelector(`button[data-all="${dim}"]`);
      if (btnAll) {
        btnAll.classList.toggle("act", Boolean(q));
        btnAll.title = q ? `Selecionar os ${vis} itens visíveis` : "Selecionar tudo que está visível";
      }
    };
    inp.onkeydown = (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        const btnAll = fEl.querySelector(`button[data-all="${inp.dataset.s}"]`);
        if (btnAll) btnAll.click();
      }
    };
  });

  // Botão 'T' (Selecionar tudo que está visível)
  fEl.querySelectorAll("button[data-all]").forEach(b => {
    b.onclick = () => {
      const dim = b.dataset.all;
      const s = fEl.querySelector(`select[data-dim="${dim}"]`);
      if (s && s.multiple) {
        Array.from(s.options).forEach(o => {
          if (!o.hidden && !o.disabled) o.selected = true;
        });
        readFiltersFromUI();
        sincronizarEstadoEUI();
      } else if (dim === "mes") {
        aoMudarMes();
      } else if (dim === "tipo") {
        aoMudarTipo();
      } else if (dim === "class") {
        const sc = document.getElementById("sel-global-classificador");
        if (sc) sc.value = "ALL";
        aoMudarClassificador();
      }
    };
  });

  // Botão '×' (Limpar individual)
  fEl.querySelectorAll("button[data-clr]").forEach(b => {
    b.onclick = () => {
      const dim = b.dataset.clr;
      const s = fEl.querySelector(`select[data-dim="${dim}"]`);
      if (s && s.multiple) {
        Array.from(s.options).forEach(o => { o.selected = false; o.hidden = false; });
        const inp = fEl.querySelector(`input[data-s="${dim}"]`);
        if (inp) inp.value = "";
        readFiltersFromUI();
        sincronizarEstadoEUI();
      }
    };
  });

  // Listener nativo de mudança nos selects múltiplos
  ["seg", "prod", "reg"].forEach(dim => {
    const s = fEl.querySelector(`select[data-dim="${dim}"]`);
    if (s) {
      s.onchange = () => {
        readFiltersFromUI();
        sincronizarEstadoEUI();
      };
    }
  });
}

function readFiltersFromUI() {
  const sSeg = document.getElementById("sel-mult-seg");
  if (sSeg) {
    appState.segmentos = new Set(Array.from(sSeg.selectedOptions).map(o => o.value));
  }
  const sProd = document.getElementById("sel-mult-prod");
  if (sProd) {
    appState.produtos = new Set(Array.from(sProd.selectedOptions).map(o => o.value));
  }
  const sReg = document.getElementById("sel-mult-reg");
  if (sReg) {
    appState.regionais = new Set(Array.from(sReg.selectedOptions).map(o => o.value));
  }
}

function popularSeletoresPeriodo() {
  const selMes = document.getElementById("sel-global-mes");
  if (!selMes) return;
  selMes.innerHTML = "";
  
  (DATA.meses_seletores || []).forEach(m => {
    const opt = document.createElement("option");
    opt.value = m.mes;
    opt.textContent = m.rotulo;
    if (m.mes === appState.mes) opt.selected = true;
    selMes.appendChild(opt);
  });
  
  atualizarOpcoesTendencia();
}

function atualizarOpcoesTendencia() {
  const selTipo = document.getElementById("sel-global-tipo");
  if (!selTipo) return;
  selTipo.innerHTML = "";
  
  const mObj = (DATA.meses_seletores || []).find(m => m.mes === appState.mes);
  const tipos = mObj ? mObj.tipos : ["TEND2", "TEND1"];
  
  tipos.forEach(t => {
    const opt = document.createElement("option");
    opt.value = t;
    opt.textContent = t;
    if (t === appState.tipo) opt.selected = true;
    selTipo.appendChild(opt);
  });
  
  if (!tipos.includes(appState.tipo)) {
    appState.tipo = mObj ? mObj.tipo_padrao : tipos[0];
    selTipo.value = appState.tipo;
  }
}

function aoMudarMes() {
  const selMes = document.getElementById("sel-global-mes");
  if (selMes) appState.mes = selMes.value;
  atualizarOpcoesTendencia();
  sincronizarEstadoEUI();
}

function aoMudarTipo() {
  const selTipo = document.getElementById("sel-global-tipo");
  if (selTipo) appState.tipo = selTipo.value;
  sincronizarEstadoEUI();
}

function aoMudarClassificador() {
  const selCls = document.getElementById("sel-global-classificador");
  if (selCls) appState.classificadorFiltro = selCls.value;
  sincronizarEstadoEUI();
}

function removerFiltro(dim, val) {
  if (dim === "seg") {
    appState.segmentos.delete(val);
    const s = document.getElementById("sel-mult-seg");
    if (s) Array.from(s.options).forEach(o => { if (o.value === val) o.selected = false; });
  } else if (dim === "prod") {
    appState.produtos.delete(val);
    const s = document.getElementById("sel-mult-prod");
    if (s) Array.from(s.options).forEach(o => { if (o.value === val) o.selected = false; });
  } else if (dim === "reg") {
    appState.regionais.delete(val);
    const s = document.getElementById("sel-mult-reg");
    if (s) Array.from(s.options).forEach(o => { if (o.value === val) o.selected = false; });
  } else if (dim === "class") {
    appState.classificadorFiltro = "ALL";
    const s = document.getElementById("sel-global-classificador");
    if (s) s.value = "ALL";
  }
  sincronizarEstadoEUI();
}

function resetarTodosFiltros() {
  appState.mes = "202610";
  appState.tipo = "TEND2";
  appState.segmentos = new Set(["CONS", "PME", "GE"]);
  appState.produtos = new Set(["CTL", "POS", "FLX", "PRE"]);
  appState.regionais = new Set(["CLARO NO"]);
  appState.classificadorFiltro = "ALL";

  const selMes = document.getElementById("sel-global-mes");
  if (selMes) selMes.value = "202610";
  atualizarOpcoesTendencia();

  const sSeg = document.getElementById("sel-mult-seg");
  if (sSeg) Array.from(sSeg.options).forEach(o => { o.selected = true; o.hidden = false; });

  const sProd = document.getElementById("sel-mult-prod");
  if (sProd) Array.from(sProd.options).forEach(o => { o.selected = true; o.hidden = false; });

  const sReg = document.getElementById("sel-mult-reg");
  if (sReg) Array.from(sReg.options).forEach(o => { o.selected = (o.value === "CLARO NO"); o.hidden = false; });

  const selCls = document.getElementById("sel-global-classificador");
  if (selCls) selCls.value = "ALL";

  sincronizarEstadoEUI();
}

// ----------------------------------------------------------------------
// MOTOR DE CÁLCULO DIMENSIONAL OFICIAL PARA SELEÇÃO MÚLTIPLA
// ----------------------------------------------------------------------
function calcularMetricaRecorte(row) {
  if (!row || !row.valores) return 0;
  const v = row.valores;

  const segs = appState.segmentos;
  const prods = appState.produtos;

  const allSegs = segs.size === 0 || (segs.has("CONS") && segs.has("PME") && segs.has("GE"));
  const allProds = prods.size === 0 || (prods.has("CTL") && prods.has("POS") && prods.has("FLX") && prods.has("PRE"));

  if (allSegs && allProds) {
    return v["Total"] !== undefined ? v["Total"] : 0;
  }

  let total = 0;

  // Consumo Massivo (PF)
  if (segs.size === 0 || segs.has("CONS")) {
    if (allProds) {
      total += (v["Total Consumo"] || 0);
    } else {
      if (prods.has("CTL")) total += (v["Controle (AUTOC + CTLFC)"] || 0);
      if (prods.has("POS")) total += (v["CONSUMO - Conta"] || 0);
      if (prods.has("FLX")) total += (v["Flex"] || 0);
      if (prods.has("PRE")) total += (v["Pré-pago"] || 0);
    }
  }

  // PME (PE + ME)
  if (segs.size === 0 || segs.has("PME")) {
    if (allProds) {
      total += (v["PE +ME - Total PE + ME"] || 0);
    } else {
      if (prods.has("POS")) total += (v["PE - Conta PME"] || 0) + (v["ME - Conta PME"] || 0);
      if (prods.has("FLX")) total += (v["Flex PE"] || 0) + (v["Flex ME"] || 0);
    }
  }

  // Grandes Empresas (GE)
  if (segs.size === 0 || segs.has("GE")) {
    if (allProds) {
      total += (v["Pós-pago GE"] || 0);
    } else {
      if (prods.has("POS")) total += (v["GE - Conta"] || 0);
    }
  }

  return total;
}

// ----------------------------------------------------------------------
// SINCRONIZAÇÃO COMPLETA DE ESTADO E RENDERIZAÇÃO UNIVERSAL
// ----------------------------------------------------------------------
function sincronizarEstadoEUI() {
  const mObj = (DATA.meses_seletores || []).find(m => m.mes === appState.mes);
  const rotuloMes = mObj ? mObj.rotulo : appState.mes;

  // Mapas de Rótulos
  const mapSeg = { "CONS": "Consumo (PF)", "PME": "PME (PE+ME)", "GE": "Grandes Emp" };
  const mapProd = { "CTL": "Controle", "POS": "Pós/Conta", "FLX": "Flex", "PRE": "Pré-pago" };
  const mapClass = {
    "ALL": "Todas as Movimentações",
    "INVOL": "Abertura Churn Involuntário",
    "MIG": "Abertura Migrações",
    "GROSS": "Gross & Ativações",
    "RESUMO": "Resumo Executivo"
  };

  const segText = appState.segmentos.size === 3 ? "Todos" : Array.from(appState.segmentos).map(s => mapSeg[s] || s).join(", ") || "(nenhum)";
  const prodText = appState.produtos.size === 4 ? "Todos" : Array.from(appState.produtos).map(p => mapProd[p] || p).join(", ") || "(nenhum)";
  const regText = appState.regionais.size === 0 ? "Todas" : Array.from(appState.regionais).map(r => r.replace("CLARO ", "")).join(", ");

  // Atualizar Badges do Header
  const subMes = document.getElementById("sub-lbl-mes");
  const subTipo = document.getElementById("sub-lbl-tipo");
  const subSeg = document.getElementById("sub-lbl-seg");
  const subProd = document.getElementById("sub-lbl-prod");
  const subReg = document.getElementById("sub-lbl-reg");

  if (subMes) subMes.textContent = rotuloMes;
  if (subTipo) subTipo.textContent = appState.tipo;
  if (subSeg) subSeg.textContent = segText;
  if (subProd) subProd.textContent = prodText;
  if (subReg) subReg.textContent = regText;

  // Atualizar Contadores (.cnt)
  const cntMes = document.getElementById("cntMes");
  const cntTipo = document.getElementById("cntTipo");
  const cntSeg = document.getElementById("cntSeg");
  const cntProd = document.getElementById("cntProd");
  const cntReg = document.getElementById("cntReg");

  if (cntMes) cntMes.textContent = appState.mes;
  if (cntTipo) cntTipo.textContent = appState.tipo;
  if (cntSeg) cntSeg.textContent = appState.segmentos.size === 3 ? "Todos (3)" : `${appState.segmentos.size}/3`;
  if (cntProd) cntProd.textContent = appState.produtos.size === 4 ? "Todos (4)" : `${appState.produtos.size}/4`;
  if (cntReg) cntReg.textContent = `${appState.regionais.size} reg`;

  // Atualizar Rodapés .sel de Cada Filtro
  const dSeg = document.getElementById("sel_desc_seg");
  const dProd = document.getElementById("sel_desc_prod");
  const dReg = document.getElementById("sel_desc_reg");
  if (dSeg) dSeg.textContent = segText;
  if (dProd) dProd.textContent = prodText;
  if (dReg) dReg.textContent = regText;

  // Atualizar Chips Dinâmicos
  const chipsHost = document.getElementById("chips");
  if (chipsHost) {
    let chipsHtml = `
      <span class="chip">Mês: ${rotuloMes}</span>
      <span class="chip">Modelo: ${appState.tipo}</span>
    `;
    if (appState.segmentos.size < 3) {
      appState.segmentos.forEach(s => {
        chipsHtml += `<span class="chip">Seg: ${mapSeg[s]} <i onclick="removerFiltro('seg','${s}')">×</i></span>`;
      });
    }
    if (appState.produtos.size < 4) {
      appState.produtos.forEach(p => {
        chipsHtml += `<span class="chip">Prod: ${mapProd[p]} <i onclick="removerFiltro('prod','${p}')">×</i></span>`;
      });
    }
    if (appState.classificadorFiltro !== "ALL") {
      chipsHtml += `<span class="chip">Class: ${mapClass[appState.classificadorFiltro]} <i onclick="removerFiltro('class','')">×</i></span>`;
    }
    chipsHost.innerHTML = chipsHtml;
  }

  // Notificar Resumo do Drawer
  const fSummary = document.getElementById("fSummary");
  if (fSummary) {
    fSummary.textContent = `${rotuloMes} · ${appState.tipo} · Seg: ${segText} · Prod: ${prodText}`;
  }

  // Renderizar Todos os Componentes e Tabelas Analíticas (100% Reativas)
  drawKpis();
  renderExecutivo();
  renderNetAddsTable();
  renderSegmentoTable();
  renderB2BTable();
  renderMatrizMigracao();
  renderHistoricoTable();
}

// ----------------------------------------------------------------------
// 1. CARDS DE KPI (PADRÃO CHURN SAFRA — 100% CONECTADOS AOS DADOS REAIS)
// ----------------------------------------------------------------------
function drawKpis() {
  const host = document.getElementById("kpis");
  if (!host) return;

  const seg2 = DATA.segmento_tend2 || [];

  const rowGross2 = seg2.find(r => r.metrica === "Gross Bruto");
  const rowDesc2 = seg2.find(r => r.metrica === "Descontos");
  const rowGrossLiq2 = seg2.find(r => r.metrica === "Gross Líquido");
  const rowInvolTot2 = seg2.find(r => r.metrica === "Churn Involuntário Total");
  const rowVol2 = seg2.find(r => r.metrica === "Churn Voluntário");
  const rowMigNet2 = seg2.find(r => r.metrica === "Migração Net");
  const rowNet2 = seg2.find(r => r.metrica === "Net adds");

  const grossNO = calcularMetricaRecorte(rowGross2);
  const descNO = calcularMetricaRecorte(rowDesc2);
  const grossLiqNO = calcularMetricaRecorte(rowGrossLiq2);
  const involNO = calcularMetricaRecorte(rowInvolTot2);
  const volNO = calcularMetricaRecorte(rowVol2);
  const migNO = calcularMetricaRecorte(rowMigNet2);
  const netNO = calcularMetricaRecorte(rowNet2);

  // Benchmarks Brasil (Total Nacional correspondente)
  const grossBR = rowGross2 && rowGross2.valores ? (rowGross2.valores["Total"] || 1) : 1;
  const netBR = rowNet2 && rowNet2.valores ? (rowNet2.valores["Total"] || 1) : 1;
  const shareNet = netBR !== 0 ? (netNO / netBR * 100) : 0;

  const isParc = appState.tipo.includes("TEND");
  const P = isParc ? ' <span class="pc">tendência</span>' : '';

  const card = (k, v, d, cls="") => `
    <div class="kpi ${cls}${isParc ? ' parc' : ''}">
      <div class="k">${k}${P}</div>
      <div class="v">${v}</div>
      <div class="d">${d}</div>
    </div>
  `;

  host.innerHTML =
    card("1. Gross Bruto", fmtInt(grossNO), `Conversão: ${fmt(grossLiqNO / (grossNO || 1) * 100)}%`, "pos") +
    card("2. Descontos & Fakes", (descNO < 0 ? "" : "-") + fmtInt(Math.abs(descNO)), `${fmt(Math.abs(descNO) / (grossNO || 1) * 100)}% do Gross`, "acc") +
    card("3. Gross Líquido", fmtInt(grossLiqNO), "Adições Efetivas", "pos") +
    card("4. Churn Involuntário", (involNO < 0 ? "" : "-") + fmtInt(Math.abs(involNO)), "Inad, Fraude, FPD, Limpeza", "acc") +
    card("5. Churn Voluntário", (volNO < 0 ? "" : "-") + fmtInt(Math.abs(volNO)), "Cancelamento Ativo", "acc") +
    card("6. Saldo de Migrações", (migNO >= 0 ? "+" : "") + fmtInt(migNO), "Saldo Líquido (In - Out)", "np") +
    card("7. Net Adds Consolidado", (netNO >= 0 ? "+" : "") + fmtInt(netNO), netNO >= 0 ? "Saldo Positivo" : "Evasão Líquida", netNO >= 0 ? "pos" : "acc") +
    card("8. Benchmark Brasil & Share", fmtPct(shareNet), `Foco: ${fmt(netNO/1000)}k / BR: ${fmt(netBR/1000)}k`);
}

// ----------------------------------------------------------------------
// 2. SUMÁRIO EXECUTIVO (SEM METAS, COM ABERTURAS COMPLETAS E REATIVO)
// ----------------------------------------------------------------------
function renderExecutivo() {
  const thead = document.querySelector("#tbl-executivo thead");
  const tbody = document.querySelector("#tbl-executivo tbody");
  const bannerContainer = document.getElementById("exec-banner-container");
  if (!thead || !tbody) return;
  thead.innerHTML = "";
  tbody.innerHTML = "";

  const clsFiltro = appState.classificadorFiltro;

  if (bannerContainer) {
    if (appState.segmentos.size < 3 || appState.produtos.size < 4 || clsFiltro !== "ALL") {
      bannerContainer.innerHTML = `
        <div class="info-banner">
          <span>▶ Sumário Executivo filtrado para <b>${appState.segmentos.size}/3 segmentos</b> e <b>${appState.produtos.size}/4 produtos</b>. Valores recalculados com precisão matemática em tempo real.</span>
          <button class="btn-action" style="padding:4px 8px;font-size:11px" onclick="resetarTodosFiltros()">Restaurar Todas as Dimensões</button>
        </div>
      `;
    } else {
      bannerContainer.innerHTML = "";
    }
  }

  thead.innerHTML = `
    <tr>
      <th class="l sortable" style="width: 260px;" onclick="sortTable('tbl-executivo', 0)">Linha de Movimentação</th>
      <th class="sortable th-foco" style="width: 120px;" onclick="sortTable('tbl-executivo', 1)">2ª Tendência (TEND2)</th>
      <th class="sortable" style="width: 120px;" onclick="sortTable('tbl-executivo', 2)">1ª Tendência (TEND1)</th>
      <th class="sortable" style="width: 120px;" onclick="sortTable('tbl-executivo', 3)">Delta (DIFF)</th>
      <th class="th-hist-start sortable" style="width: 130px;" onclick="sortTable('tbl-executivo', 4)">Total Brasil (BR)</th>
      <th class="c sortable" style="width: 95px;" onclick="sortTable('tbl-executivo', 5)">Share NO %</th>
    </tr>
  `;

  const seg2 = DATA.segmento_tend2 || [];
  const seg1 = DATA.segmento_tend1 || [];
  const segDiff = DATA.segmento_diff || [];

  const linhasConfig = [
    // GRUPO GROSS
    { metrica: "Gross Bruto", grp: "GROSS", nivel: 1, rotulo: "1. Gross Bruto (Ativações Totais)" },
    { metrica: "Descontos", grp: "GROSS", nivel: 2, rotulo: "2. (-) Descontos & Fakes" },
    { metrica: "Gross Líquido", grp: "GROSS", nivel: 1, rotulo: "3. (=) Gross Líquido", isSubtotal: true },

    // GRUPO CHURN INVOLUNTÁRIO (ABERTURAS ANALÍTICAS)
    { metrica: "Churn Involuntário", grp: "INVOL", nivel: 2, rotulo: "4. (-) Churn Involuntário (Inadimplência)" },
    { metrica: "Fraude", grp: "INVOL", nivel: 2, rotulo: "5. (-) Fraude" },
    { metrica: "FPD", grp: "INVOL", nivel: 2, rotulo: "6. (-) FPD (First Payment Default)" },
    { metrica: "Limpeza", grp: "INVOL", nivel: 2, rotulo: "7. (-) Limpeza Street Seller" },
    { metrica: "Churn Involuntário Total", grp: "INVOL", nivel: 1, rotulo: "8. (=) Subtotal Churn Involuntário", isSubtotal: true },

    // GRUPO CHURN VOLUNTÁRIO
    { metrica: "Churn Voluntário", grp: "VOL", nivel: 2, rotulo: "9. (-) Churn Voluntário (Cancelamento a Pedido)" },
    { metrica: "Churn total", grp: "CHURN_TOT", nivel: 1, rotulo: "10. (=) Total Churn Evasões", isSubtotal: true },

    // GRUPO MIGRAÇÕES (ABERTURAS ANALÍTICAS IN VS OUT)
    { metrica: "Migração In total", grp: "MIG", nivel: 1, rotulo: "11. (+) Migração In Total" },
    { metrica: "Migração In Side Controle", grp: "MIG", nivel: 3, rotulo: "• In Side Controle" },
    { metrica: "Migração In Outros", grp: "MIG", nivel: 3, rotulo: "• In Outros" },
    { metrica: "Migração Out total", grp: "MIG", nivel: 1, rotulo: "12. (-) Migração Out Total" },
    { metrica: "Migração Out Side", grp: "MIG", nivel: 3, rotulo: "• Out Side" },
    { metrica: "Migração Out Up", grp: "MIG", nivel: 3, rotulo: "• Out Up (Upgrade)" },
    { metrica: "Migração Out Down", grp: "MIG", nivel: 3, rotulo: "• Out Down (Downgrade)" },
    { metrica: "Migração Out Down Reversa", grp: "MIG", nivel: 3, rotulo: "• Out Down Reversa" },
    { metrica: "Migração Out Side Controle", grp: "MIG", nivel: 3, rotulo: "• Out Side Controle" },
    { metrica: "Anomalia Migrações", grp: "MIG", nivel: 2, rotulo: "13. (~) Anomalia Migrações" },
    { metrica: "Migração Net", grp: "MIG", nivel: 1, rotulo: "14. (=) Saldo Migrações (Migração Net)", isSubtotal: true },

    // RESULTADO LÍQUIDO CONSOLIDADO
    { metrica: "Net adds", grp: "NET", nivel: 1, rotulo: "15. (=) Net Adds Consolidado", isTotal: true }
  ];

  linhasConfig.forEach(cfg => {
    if (clsFiltro === "INVOL" && cfg.grp !== "INVOL") return;
    if (clsFiltro === "MIG" && cfg.grp !== "MIG") return;
    if (clsFiltro === "GROSS" && cfg.grp !== "GROSS") return;
    if (clsFiltro === "RESUMO" && !cfg.isSubtotal && !cfg.isTotal) return;

    const r2 = seg2.find(r => r.metrica === cfg.metrica);
    const r1 = seg1.find(r => r.metrica === cfg.metrica);
    const rD = segDiff.find(r => r.metrica === cfg.metrica);

    const val2 = calcularMetricaRecorte(r2);
    const val1 = calcularMetricaRecorte(r1);
    const valDiff = rD ? calcularMetricaRecorte(rD) : (val2 - val1);

    const valBR = r2 && r2.valores ? (r2.valores["Total"] || 0) : 0;
    const share = valBR !== 0 ? (val2 / valBR * 100) : 0;

    const tr = document.createElement("tr");
    if (cfg.isTotal) tr.className = "grp-total-row";
    else if (cfg.isSubtotal) tr.className = "grp-header";

    let indentClass = "";
    if (cfg.nivel === 2) indentClass = "indent-sub";
    else if (cfg.nivel === 3) indentClass = "indent-sub2";

    const corDiff = valDiff > 0 ? "var(--green)" : (valDiff < 0 ? "var(--red)" : "var(--ink2)");

    tr.innerHTML = `
      <td class="l ${indentClass}"><b>${cfg.rotulo}</b></td>
      <td class="td-foco" style="font-weight:${cfg.isTotal ? '900' : '700'}">${fmt(val2)}</td>
      <td>${fmt(val1)}</td>
      <td style="color:${corDiff};font-weight:700">${valDiff > 0 ? '+' : ''}${fmt(valDiff)}</td>
      <td class="td-hist-start" style="color:var(--ink2)">${fmt(valBR)}</td>
      <td class="c">${fmtPct(share)}</td>
    `;
    tbody.appendChild(tr);
  });
}

// ----------------------------------------------------------------------
// 3. NET ADDS REGIONAL (RANKING REATIVO POR RECORTE DE PRODUTO E SEGMENTO APARTADOS)
// ----------------------------------------------------------------------
function renderNetAddsTable() {
  const thead = document.querySelector("#tbl-netadds thead");
  const tbody = document.querySelector("#tbl-netadds tbody");
  const tfoot = document.querySelector("#tbl-netadds tfoot");
  const bannerContainer = document.getElementById("netadds-banner-container");
  if (!thead || !tbody || !tfoot) return;

  const segs = appState.segmentos;
  const prods = appState.produtos;

  // Função para calcular o Net Adds filtrado para uma dada Regional
  function calcNetRegional(r) {
    let tot = 0;
    const allSegs = segs.size === 0 || (segs.has("CONS") && segs.has("PME") && segs.has("GE"));
    const allProds = prods.size === 0 || (prods.has("CTL") && prods.has("POS") && prods.has("FLX") && prods.has("PRE"));

    if (allSegs && allProds) return r.total_geral || 0;

    if (segs.size === 0 || segs.has("CONS")) {
      if (allProds) {
        tot += (r.total_consumo || 0);
      } else {
        if (prods.has("CTL")) tot += (r.controle_total || 0);
        if (prods.has("POS")) tot += (r.conta || 0) + (r.bl_pos_total || 0);
        if (prods.has("FLX")) tot += (r.flex || 0);
        if (prods.has("PRE")) tot += (r.pre_voz || 0) + (r.bl_pre || 0);
      }
    }
    if (segs.size === 0 || segs.has("PME")) {
      if (allProds) {
        tot += (r.total_pme || 0);
      } else {
        if (prods.has("POS")) tot += (r.conta_pe || 0) + (r.conta_me || 0);
      }
    }
    if (segs.size === 0 || segs.has("GE")) {
      if (allProds) {
        tot += (r.total_ge || 0);
      } else {
        if (prods.has("POS")) tot += (r.conta_ge || 0);
      }
    }
    return tot;
  }

  let labelRecorte = "Net Adds do Recorte Filtrado";
  if (bannerContainer) {
    if (segs.size < 3 || prods.size < 4) {
      bannerContainer.innerHTML = `
        <div class="info-banner">
          <span>▶ Ranking de Regionais reordenado em tempo real pelo <b>Net Adds do Recorte Selecionado</b> (${segs.size}/3 segs, ${prods.size}/4 prods).</span>
          <button class="btn-action" style="padding:4px 8px;font-size:11px" onclick="resetarTodosFiltros()">Ver Consolidado Geral</button>
        </div>
      `;
    } else {
      bannerContainer.innerHTML = "";
    }
  }

  thead.innerHTML = `
    <tr>
      <th class="c sortable" style="width: 50px;" onclick="sortTable('tbl-netadds', 0)">Rank</th>
      <th class="l sortable" style="width: 160px;" onclick="sortTable('tbl-netadds', 1)">Regional</th>
      <th class="sortable th-foco" style="width: 130px;" onclick="sortTable('tbl-netadds', 2)">${labelRecorte}</th>
      <th class="sortable" style="width: 95px;" onclick="sortTable('tbl-netadds', 3)">Conta (Pós)</th>
      <th class="sortable" style="width: 100px;" onclick="sortTable('tbl-netadds', 4)">Controle Total</th>
      <th class="sortable" style="width: 85px;" onclick="sortTable('tbl-netadds', 5)">Flex</th>
      <th class="sortable" style="width: 95px;" onclick="sortTable('tbl-netadds', 6)">Consumo Total</th>
      <th class="sortable" style="width: 95px;" onclick="sortTable('tbl-netadds', 7)">PME Total</th>
      <th class="sortable" style="width: 95px;" onclick="sortTable('tbl-netadds', 8)">GE Total</th>
      <th class="th-hist-start sortable" style="width: 120px;" onclick="sortTable('tbl-netadds', 9)">Net Adds Geral</th>
    </tr>
  `;

  tbody.innerHTML = "";
  tfoot.innerHTML = "";

  let list = (DATA.net_adds || []).filter(r => !r.regional.includes("Total"));
  const totalRow = (DATA.net_adds || []).find(r => r.regional.includes("Total"));

  list.sort((a, b) => calcNetRegional(b) - calcNetRegional(a));

  list.forEach((r, idx) => {
    const tr = document.createElement("tr");
    const isFocoReg = (appState.regionais.has("CLARO NO") && (r.sigla === "NO" || r.regional.includes("CLARO NO"))) ||
                      appState.regionais.has(r.regional);

    if (isFocoReg) tr.className = "row-foco";

    const valRecorte = calcNetRegional(r);

    tr.innerHTML = `
      <td class="c"><b>${idx + 1}º</b></td>
      <td class="l">
        <span class="badge-reg ${r.sigla === 'NO' ? 'no' : ''}">${r.sigla}</span>
        ${r.regional}
      </td>
      <td class="td-foco" style="font-weight:800;color:${valRecorte >= 0 ? 'var(--green)' : 'var(--red)'}">
        ${fmt(valRecorte)}
      </td>
      <td>${fmt(r.conta)}</td>
      <td><b>${fmt(r.controle_total)}</b></td>
      <td>${fmt(r.flex)}</td>
      <td><b>${fmt(r.total_consumo)}</b></td>
      <td><b>${fmt(r.total_pme)}</b></td>
      <td><b>${fmt(r.total_ge)}</b></td>
      <td class="th-hist-start" style="font-weight:800;color:${r.total_geral >= 0 ? 'var(--green)' : 'var(--red)'}">
        ${fmt(r.total_geral)}
      </td>
    `;
    tbody.appendChild(tr);
  });

  if (totalRow) {
    const trTot = document.createElement("tr");
    trTot.className = "grp-total-row";
    const totRecorte = calcNetRegional(totalRow);

    trTot.innerHTML = `
      <td class="c">●</td>
      <td class="l"><b>${totalRow.regional}</b></td>
      <td class="td-foco" style="font-weight:900;color:${totRecorte >= 0 ? 'var(--green)' : 'var(--red)'}">
        ${fmt(totRecorte)}
      </td>
      <td>${fmt(totalRow.conta)}</td>
      <td><b>${fmt(totalRow.controle_total)}</b></td>
      <td>${fmt(totalRow.flex)}</td>
      <td><b>${fmt(totalRow.total_consumo)}</b></td>
      <td><b>${fmt(totalRow.total_pme)}</b></td>
      <td><b>${fmt(totalRow.total_ge)}</b></td>
      <td class="th-hist-start" style="font-weight:900;color:${totalRow.total_geral >= 0 ? 'var(--green)' : 'var(--red)'}">
        ${fmt(totalRow.total_geral)}
      </td>
    `;
    tfoot.appendChild(trTot);
  }
}

// ----------------------------------------------------------------------
// 4. DESDOBRAMENTO POR SEGMENTO (22 LINHAS E COLUNAS DINÂMICAS)
// ----------------------------------------------------------------------
function renderSegmentoTable() {
  const segData = (appState.tipo === "TEND1" ? DATA.segmento_tend1 : DATA.segmento_tend2) || [];
  if (!segData || !segData.length) return;

  const thead = document.querySelector("#tbl-segmento thead");
  const tbody = document.querySelector("#tbl-segmento tbody");
  const bannerContainer = document.getElementById("segmento-banner-container");
  if (!thead || !tbody) return;
  thead.innerHTML = "";
  tbody.innerHTML = "";

  const sampleCols = Object.keys(segData[0].valores);
  let displayCols = sampleCols.filter(c => {
    // Verificar se pertence a algum segmento selecionado
    let matchSeg = false;
    if (appState.segmentos.size === 0 || appState.segmentos.size === 3) matchSeg = true;
    else {
      if (appState.segmentos.has("CONS") && (c.includes("CONSUMO") || c.includes("Controle") || c.includes("Flex") || c.includes("Consumo") || c.includes("Pré"))) matchSeg = true;
      if (appState.segmentos.has("PME") && (c.includes("PE") || c.includes("ME") || c.includes("PME"))) matchSeg = true;
      if (appState.segmentos.has("GE") && c.includes("GE")) matchSeg = true;
    }
    if (!matchSeg) return false;

    // Verificar se pertence a algum produto selecionado
    if (appState.produtos.size === 0 || appState.produtos.size === 4) return true;
    const cLow = c.toLowerCase();
    if (appState.produtos.has("CTL") && (cLow.includes("controle") || cLow.includes("autoc") || cLow.includes("ctlfc"))) return true;
    if (appState.produtos.has("POS") && (cLow.includes("conta") || cLow.includes("pós") || cLow.includes("pos"))) return true;
    if (appState.produtos.has("FLX") && (cLow.includes("flex") || cLow.includes("flx"))) return true;
    if (appState.produtos.has("PRE") && (cLow.includes("pré") || cLow.includes("pre"))) return true;
    return false;
  });

  if (!displayCols.length) displayCols = sampleCols.slice(0, 10);

  if (bannerContainer) {
    if (appState.segmentos.size < 3 || appState.produtos.size < 4) {
      bannerContainer.innerHTML = `
        <div class="info-banner">
          <span>▶ Exibindo <b>${displayCols.length}</b> colunas analíticas e consolidado filtrado para o recorte de seleção múltipla ativo.</span>
          <button class="btn-action" style="padding:4px 8px;font-size:11px" onclick="resetarTodosFiltros()">Exibir Todas as Colunas</button>
        </div>
      `;
    } else {
      bannerContainer.innerHTML = "";
    }
  }

  let thHtml = `<tr>
    <th class="l sortable" style="width:240px" onclick="sortTable('tbl-segmento', 0)">Linha de Movimentação</th>
    <th class="sortable th-foco" style="width:125px" onclick="sortTable('tbl-segmento', 1)">Total do Recorte</th>
  `;
  displayCols.forEach((c, i) => {
    thHtml += `<th class="sortable" style="width:115px" onclick="sortTable('tbl-segmento', ${i+2})">${c.replace("CONSUMO - ", "").replace("CLARO - ", "")}</th>`;
  });
  thHtml += `</tr>`;
  thead.innerHTML = thHtml;

  segData.forEach(row => {
    const tr = document.createElement("tr");
    const mNome = row.metrica;
    if (mNome.includes("Net adds") || mNome.includes("Total")) tr.className = "grp-total-row";
    else if (mNome.includes("Líquido") || mNome.includes("Saldo")) tr.className = "grp-header";

    const somaRecorte = calcularMetricaRecorte(row);

    let tds = `<td class="l"><b>${mNome}</b></td>
               <td class="td-foco" style="font-weight:800">${fmt(somaRecorte)}</td>`;
    displayCols.forEach(c => {
      const val = row.valores[c];
      tds += `<td>${fmt(val)}</td>`;
    });
    tr.innerHTML = tds;
    tbody.appendChild(tr);
  });
}

// ----------------------------------------------------------------------
// 5. B2B CORPORATIVO (LENDO DIRETO DE DATA.b2b — 22 LINHAS ANALÍTICAS)
// ----------------------------------------------------------------------
function renderB2BTable() {
  const thead = document.querySelector("#tbl-b2b thead");
  const tbody = document.querySelector("#tbl-b2b tbody");
  const bannerContainer = document.getElementById("b2b-banner-container");
  if (!thead || !tbody) return;
  thead.innerHTML = "";
  tbody.innerHTML = "";

  const showPme = appState.segmentos.size === 0 || appState.segmentos.has("PME");
  const showGe = appState.segmentos.size === 0 || appState.segmentos.has("GE");

  if (bannerContainer) {
    if (!showPme && !showGe) {
      bannerContainer.innerHTML = `
        <div class="info-banner">
          <span>ℹ O filtro global ativo inclui apenas <b>Consumo Massivo (PF)</b>. A tabela abaixo exibe o segmento corporativo B2B (PME + GE).</span>
          <button class="btn-action" style="padding:4px 8px;font-size:11px" onclick="resetarTodosFiltros()">Adicionar PME e GE ao Filtro</button>
        </div>
      `;
    } else {
      bannerContainer.innerHTML = "";
    }
  }

  let thHtml = `<tr><th class="l sortable" style="width: 240px;" onclick="sortTable('tbl-b2b', 0)">Linha de Movimentação B2B</th>`;

  if (showPme) {
    thHtml += `
      <th class="sortable" style="width: 90px;" onclick="sortTable('tbl-b2b', 1)">PE Conta</th>
      <th class="sortable" style="width: 90px;" onclick="sortTable('tbl-b2b', 2)">PE BL</th>
      <th class="sortable" style="width: 95px;" onclick="sortTable('tbl-b2b', 3)">Total PE</th>
      <th class="sortable" style="width: 90px;" onclick="sortTable('tbl-b2b', 4)">ME Conta</th>
      <th class="sortable" style="width: 90px;" onclick="sortTable('tbl-b2b', 5)">ME BL</th>
      <th class="sortable" style="width: 95px;" onclick="sortTable('tbl-b2b', 6)">Total ME</th>
      <th class="sortable th-foco" style="width: 110px;" onclick="sortTable('tbl-b2b', 7)">Total PME</th>
    `;
  }

  if (showGe) {
    thHtml += `
      <th class="sortable" style="width: 95px;" onclick="sortTable('tbl-b2b', 8)">GE Com Conta</th>
      <th class="sortable" style="width: 95px;" onclick="sortTable('tbl-b2b', 9)">GE Telem</th>
      <th class="sortable" style="width: 105px;" onclick="sortTable('tbl-b2b', 10)">GE Com Total</th>
      <th class="sortable" style="width: 105px;" onclick="sortTable('tbl-b2b', 11)">GE Sem Total</th>
    `;
  }

  thHtml += `<th class="th-hist-start sortable" style="width: 125px;" onclick="sortTable('tbl-b2b', 12)">Consolidado B2B</th></tr>`;
  thead.innerHTML = thHtml;

  const b2bData = DATA.b2b || [];

  b2bData.forEach(r => {
    const tr = document.createElement("tr");
    const mNome = r.metrica;
    const v = r.valores || {};

    if (mNome.includes("Net adds") || mNome.includes("Total")) tr.className = "grp-total-row";
    else if (mNome.includes("Líquido") || mNome.includes("Saldo")) tr.className = "grp-header";

    const peConta = v["pe_conta"] || 0;
    const peBl = v["pe_bl"] || 0;
    const peTot = v["pe_total"] || (peConta + peBl);
    const meConta = v["me_conta"] || 0;
    const meBl = v["me_bl"] || 0;
    const meTot = v["me_total"] || (meConta + meBl);
    const pmeTot = v["pme_total"] || (peTot + meTot);

    const geComConta = v["ge_com_conta"] || 0;
    const geTelem = v["ge_com_telem"] || 0;
    const geComTot = v["ge_com_total"] || (geComConta + geTelem);
    const geSemTot = v["ge_sem_total"] || 0;

    let totB2B = 0;
    if (showPme) totB2B += pmeTot;
    if (showGe) totB2B += (geComTot + geSemTot);

    let tds = `<td class="l"><b>${mNome}</b></td>`;

    if (showPme) {
      tds += `
        <td>${fmt(peConta)}</td>
        <td>${fmt(peBl)}</td>
        <td><b>${fmt(peTot)}</b></td>
        <td>${fmt(meConta)}</td>
        <td>${fmt(meBl)}</td>
        <td><b>${fmt(meTot)}</b></td>
        <td class="td-foco"><b>${fmt(pmeTot)}</b></td>
      `;
    }

    if (showGe) {
      tds += `
        <td>${fmt(geComConta)}</td>
        <td>${fmt(geTelem)}</td>
        <td><b>${fmt(geComTot)}</b></td>
        <td><b>${fmt(geSemTot)}</b></td>
      `;
    }

    tds += `<td class="th-hist-start" style="font-weight:800;color:${totB2B >= 0 ? 'var(--green)' : 'var(--red)'}">${fmt(totB2B)}</td>`;

    tr.innerHTML = tds;
    tbody.appendChild(tr);
  });
}

// ----------------------------------------------------------------------
// 6. MATRIZ DE MIGRAÇÃO (FILTRAGEM POR SEGMENTO E PRODUTO)
// ----------------------------------------------------------------------
function renderMatrizMigracao() {
  const thead = document.querySelector("#tbl-matriz-migracao thead");
  const tbody = document.querySelector("#tbl-matriz-migracao tbody");
  const tfoot = document.querySelector("#tbl-matriz-migracao tfoot");
  const bannerContainer = document.getElementById("migracao-banner-container");
  if (!thead || !tbody || !tfoot) return;
  thead.innerHTML = "";
  tbody.innerHTML = "";
  tfoot.innerHTML = "";

  const segs = appState.segmentos;
  const prods = appState.produtos;

  let mList = (DATA.matriz_migracao || []).filter(r => {
    // Filtro por Segmento de Origem
    if (segs.size > 0 && segs.size < 3) {
      if (r.mercado === "CONSUMO" && !segs.has("CONS")) return false;
      if (r.mercado === "PME" && !segs.has("PME")) return false;
      if (r.mercado === "GE" && !segs.has("GE")) return false;
    }
    // Filtro por Produto de Origem
    if (prods.size > 0 && prods.size < 4) {
      const orig = r.origem.toLowerCase();
      let matchP = false;
      if (prods.has("CTL") && (orig.includes("controle") || orig.includes("autoc"))) matchP = true;
      if (prods.has("POS") && (orig.includes("conta") || orig.includes("pós"))) matchP = true;
      if (prods.has("FLX") && orig.includes("flex")) matchP = true;
      if (prods.has("PRE") && orig.includes("pré")) matchP = true;
      if (!matchP) return false;
    }
    return true;
  });

  if (bannerContainer) {
    if (segs.size < 3 || prods.size < 4) {
      bannerContainer.innerHTML = `
        <div class="info-banner">
          <span>⟳ Matriz de Migração filtrada: exibindo <b>${mList.length}</b> plataformas de origem ativas na seleção múltipla.</span>
          <button class="btn-action" style="padding:4px 8px;font-size:11px" onclick="resetarTodosFiltros()">Exibir Todos os Fluxos</button>
        </div>
      `;
    } else {
      bannerContainer.innerHTML = "";
    }
  }

  thead.innerHTML = `
    <tr>
      <th class="l sortable" style="width: 170px;" onclick="sortTable('tbl-matriz-migracao', 0)">Plataforma de Origem</th>
      <th class="th-foco sortable" style="width: 110px;" onclick="sortTable('tbl-matriz-migracao', 1)">Total Migrado (Out)</th>
      <th class="sortable" style="width: 95px;" onclick="sortTable('tbl-matriz-migracao', 2)">Para Conta</th>
      <th class="sortable" style="width: 110px;" onclick="sortTable('tbl-matriz-migracao', 3)">Para Controle</th>
      <th class="sortable" style="width: 100px;" onclick="sortTable('tbl-matriz-migracao', 4)">Para CTL Fácil</th>
      <th class="sortable" style="width: 90px;" onclick="sortTable('tbl-matriz-migracao', 5)">Para Flex</th>
      <th class="sortable" style="width: 95px;" onclick="sortTable('tbl-matriz-migracao', 6)">Para BL PF</th>
      <th class="sortable" style="width: 95px;" onclick="sortTable('tbl-matriz-migracao', 7)">Para BL CW</th>
      <th class="sortable" style="width: 95px;" onclick="sortTable('tbl-matriz-migracao', 8)">Para Pré Voz</th>
      <th class="th-hist-start sortable" style="width: 95px;" onclick="sortTable('tbl-matriz-migracao', 9)">Para PME</th>
      <th class="sortable" style="width: 95px;" onclick="sortTable('tbl-matriz-migracao', 10)">Para GE</th>
    </tr>
  `;

  let totOut = 0, totConta = 0, totAutoc = 0, totCtlfc = 0, totFlex = 0, totBlpf = 0, totBlcw = 0, totPre = 0, totPme = 0, totGe = 0;

  mList.forEach(r => {
    const tr = document.createElement("tr");
    const d = r.destinos || {};

    totOut += (r.total_out || 0);
    totConta += (d["Conta"] || 0);
    totAutoc += (d["Controle (AUTOC)"] || 0);
    totCtlfc += (d["Controle Fácil"] || 0);
    totFlex += (d["Flex"] || 0);
    totBlpf += (d["BL Pós PF"] || 0);
    totBlcw += (d["BL Pós CW"] || 0);
    totPre += (d["Pré Voz"] || 0);
    totPme += (d["Conta PME"] || 0);
    totGe += (d["Conta GE"] || 0);

    tr.innerHTML = `
      <td class="l">
        <span class="badge-reg">${r.mercado}</span>
        <b>${r.origem}</b>
      </td>
      <td class="td-foco" style="font-weight:700">${fmt(r.total_out)}</td>
      <td>${fmt(d["Conta"])}</td>
      <td>${fmt(d["Controle (AUTOC)"])}</td>
      <td>${fmt(d["Controle Fácil"])}</td>
      <td>${fmt(d["Flex"])}</td>
      <td>${fmt(d["BL Pós PF"])}</td>
      <td>${fmt(d["BL Pós CW"])}</td>
      <td>${fmt(d["Pré Voz"])}</td>
      <td class="td-hist-start">${fmt(d["Conta PME"])}</td>
      <td>${fmt(d["Conta GE"])}</td>
    `;
    tbody.appendChild(tr);
  });

  const trTot = document.createElement("tr");
  trTot.className = "grp-total-row";
  trTot.innerHTML = `
    <td class="l"><b>Total Geral Migração (Filtrado)</b></td>
    <td class="td-foco" style="font-weight:900">${fmt(totOut)}</td>
    <td>${fmt(totConta)}</td>
    <td>${fmt(totAutoc)}</td>
    <td>${fmt(totCtlfc)}</td>
    <td>${fmt(totFlex)}</td>
    <td>${fmt(totBlpf)}</td>
    <td>${fmt(totBlcw)}</td>
    <td>${fmt(totPre)}</td>
    <td class="td-hist-start">${fmt(totPme)}</td>
    <td>${fmt(totGe)}</td>
  `;
  tfoot.appendChild(trTot);
}

// ----------------------------------------------------------------------
// 7. HISTÓRICO CONSOLIDADO (12 MESES)
// ----------------------------------------------------------------------
function renderHistoricoTable() {
  const tbody = document.querySelector("#tbl-historico tbody");
  if (!tbody) return;
  tbody.innerHTML = "";

  let hList = DATA.historico || [];
  if (appState.tipo && appState.tipo !== "ALL") {
    const filtered = hList.filter(h => h.tipo === appState.tipo);
    if (filtered.length >= 3) hList = filtered;
  }

  hList.forEach(r => {
    const tr = document.createElement("tr");
    const isFoco = r.mes === appState.mes;
    if (isFoco) tr.className = "row-foco";

    tr.style.cursor = "pointer";
    tr.title = "Clique para selecionar esta safra";
    tr.onclick = () => {
      appState.mes = r.mes;
      const selMes = document.getElementById("sel-global-mes");
      if (selMes) selMes.value = r.mes;
      aoMudarMes();
    };

    const grossNO = r.gross_no || 0;
    const descNO = r.desc_no || 0;
    const grossLiqNO = r.gross_liq_no || 0;
    const involNO = r.churn_invol_no || 0;
    const volNO = r.churn_vol_no || 0;
    const churnTotNO = r.churn_tot_no || 0;
    const saldoMigNO = r.saldo_mig_no || 0;
    const netNO = r.net_adds_no || 0;
    const netBR = r.net_adds_br || 0;
    const shareGross = r.share_gross_no_pct || 0;

    tr.innerHTML = `
      <td class="l">
        <b>${r.rotulo}</b>
        ${isFoco ? '<span class="badge-reg no" style="margin-left:4px">Foco</span>' : ''}
      </td>
      <td class="c"><span class="badge-reg">${r.tipo}</span></td>
      <td>${fmt(grossNO)}</td>
      <td style="color:var(--amber)">${fmt(descNO)}</td>
      <td>${fmt(grossLiqNO)}</td>
      <td style="color:var(--red)">${fmt(involNO)}</td>
      <td style="color:var(--red)">${fmt(volNO)}</td>
      <td style="color:var(--red);font-weight:600">${fmt(churnTotNO)}</td>
      <td style="color:${saldoMigNO >= 0 ? 'var(--green)' : 'var(--red)'}">${fmt(saldoMigNO)}</td>
      <td class="td-foco" style="font-weight:800;color:${netNO >= 0 ? 'var(--green)' : 'var(--red)'}">
        ${fmt(netNO)}
      </td>
      <td class="td-hist-start" style="color:var(--ink2)">${fmt(netBR)}</td>
      <td class="c">${fmtPct(shareGross)}</td>
    `;
    tbody.appendChild(tr);
  });

  renderTemporalChart();
}

// ----------------------------------------------------------------------
// 8. GLOSSÁRIO
// ----------------------------------------------------------------------
function renderGlossario() {
  const host = document.getElementById("glossario-container");
  if (!host) return;
  host.innerHTML = "";

  (DATA.glossario || []).forEach(g => {
    const card = document.createElement("div");
    card.className = "glossary-card";
    card.innerHTML = `
      <h3>${g.indicador}</h3>
      <p><b>Conceito:</b> ${g.conceito}</p>
      <div class="formula"><b>Regra de Cálculo:</b> ${g.regra}</div>
      <p style="margin-top:6px;color:#047857"><b>Impacto Executivo:</b> ${g.impacto}</p>
    `;
    host.appendChild(card);
  });
}

// ----------------------------------------------------------------------
// 9. GRÁFICOS EM SVG NATIVO (WATERFALL & TEMPORAL COM RÓTULOS E LEGENDA)
// ----------------------------------------------------------------------
function renderWaterfall() {
  const svg = document.getElementById("svg-waterfall");
  if (!svg) return;

  const seg2 = DATA.segmento_tend2 || [];

  const rGross = seg2.find(r => r.metrica === "Gross Bruto");
  const rDesc = seg2.find(r => r.metrica === "Descontos");
  const rInvol = seg2.find(r => r.metrica === "Churn Involuntário Total");
  const rVol = seg2.find(r => r.metrica === "Churn Voluntário");
  const rMig = seg2.find(r => r.metrica === "Migração Net");
  const rNet = seg2.find(r => r.metrica === "Net adds");

  const gVal = calcularMetricaRecorte(rGross);
  const dVal = calcularMetricaRecorte(rDesc);
  const iVal = calcularMetricaRecorte(rInvol);
  const vVal = calcularMetricaRecorte(rVol);
  const mVal = calcularMetricaRecorte(rMig);
  const nVal = calcularMetricaRecorte(rNet);

  const steps = [
    { label: "1. Gross Bruto", val: gVal, type: "pos" },
    { label: "2. Descontos", val: -Math.abs(dVal), type: "neg" },
    { label: "3. Churn Invol", val: -Math.abs(iVal), type: "neg" },
    { label: "4. Churn Vol", val: -Math.abs(vVal), type: "neg" },
    { label: "5. Saldo Mig", val: mVal, type: mVal >= 0 ? "pos" : "neg" },
    { label: "6. Net Adds", val: nVal, type: "total" }
  ];

  let current = 0;
  const maxVal = Math.max(gVal, 100000) * 1.15;
  const zeroY = 220;
  const barW = 85;
  const gap = 55;
  const startX = 65;

  let barsHtml = "";

  steps.forEach((step, idx) => {
    const x = startX + idx * (barW + gap);
    let barH = Math.abs(step.val) / maxVal * 170;
    if (barH < 4) barH = 4;

    let y = 0;
    let color = "#2f7d5d";

    if (step.type === "pos") {
      y = zeroY - (current + step.val) / maxVal * 170;
      current += step.val;
      color = "#2f7d5d";
    } else if (step.type === "neg") {
      y = zeroY - current / maxVal * 170;
      current += step.val;
      color = "#c0392b";
    } else {
      y = zeroY - step.val / maxVal * 170;
      color = step.val >= 0 ? "#2a5d8f" : "#c0392b";
    }

    barsHtml += `
      <g>
        <rect x="${x}" y="${y}" width="${barW}" height="${barH}" rx="3" fill="${color}" opacity="0.9" />
        <text x="${x + barW/2}" y="${y - 8}" text-anchor="middle" font-size="11.5" font-weight="700" fill="${color}">
          ${fmt(step.val)}
        </text>
        <text x="${x + barW/2}" y="255" text-anchor="middle" font-size="11" font-weight="600" fill="#475569">
          ${step.label}
        </text>
      </g>
    `;
  });

  svg.innerHTML = `
    <line x1="40" y1="${zeroY}" x2="960" y2="${zeroY}" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="4,4" />
    ${barsHtml}
  `;
}

// Gráfico Temporal 12 Meses com RÓTULOS NUMÉRICOS (HALO BRANCO) E LEGENDA
function renderTemporalChart() {
  const svg = document.getElementById("svg-temporal");
  if (!svg) return;

  const hList = (DATA.historico || []).slice(-10);
  if (!hList.length) return;

  const maxVal = Math.max(...hList.map(h => Math.max(h.gross_liq_no || 0, Math.abs(h.net_adds_no || 0)))) * 1.35 || 320000;
  const w = 880;
  const h = 200;
  const stepX = w / (hList.length - 1 || 1);

  let ptsGross = "";
  let ptsNet = "";
  let elementsHtml = "";
  let gridHtml = "";

  hList.forEach((d, i) => {
    const x = 60 + i * stepX;
    const gVal = d.gross_liq_no || 0;
    const nVal = d.net_adds_no || 0;
    const yGross = 240 - (gVal / maxVal * h);
    const yNet = 240 - (nVal / maxVal * h);

    if (i === 0) {
      ptsGross += `M ${x} ${yGross}`;
      ptsNet += `M ${x} ${yNet}`;
    } else {
      ptsGross += ` L ${x} ${yGross}`;
      ptsNet += ` L ${x} ${yNet}`;
    }

    gridHtml += `
      <line x1="${x}" y1="20" x2="${x}" y2="240" stroke="#f1f5f9" stroke-width="1" />
      <text x="${x}" y="260" text-anchor="middle" font-size="10.5" fill="#64748b" font-weight="600">${d.rotulo.split('/')[0]}</text>
    `;

    // Círculos e Rótulos com Halo Branco (paint-order: stroke fill)
    elementsHtml += `
      <!-- Ponto e Rótulo Gross Líquido -->
      <circle cx="${x}" cy="${yGross}" r="4.5" fill="#2a5d8f" stroke="#fff" stroke-width="1.5" />
      <text x="${x}" y="${yGross - 9}" text-anchor="middle" font-size="10.5" font-weight="700" fill="#2a5d8f" stroke="#fff" stroke-width="3" paint-order="stroke fill">
        ${(gVal / 1000).toFixed(1)}k
      </text>

      <!-- Ponto e Rótulo Net Adds -->
      <circle cx="${x}" cy="${yNet}" r="4.5" fill="#0f766e" stroke="#fff" stroke-width="1.5" />
      <text x="${x}" y="${yNet - 9}" text-anchor="middle" font-size="10.5" font-weight="700" fill="#0f766e" stroke="#fff" stroke-width="3" paint-order="stroke fill">
        ${nVal >= 0 ? '+' : ''}${(nVal / 1000).toFixed(1)}k
      </text>
    `;
  });

  svg.innerHTML = `
    ${gridHtml}
    <path d="${ptsGross}" fill="none" stroke="#2a5d8f" stroke-width="3" />
    <path d="${ptsNet}" fill="none" stroke="#0f766e" stroke-width="3" stroke-dasharray="4,2" />
    ${elementsHtml}
  `;
}

// ----------------------------------------------------------------------
// EXPORTAÇÃO DE DADOS (CSV CORPORATIVO UTF-8 COM BOM)
// ----------------------------------------------------------------------
function exportarTabelaCSV() {
  const table = document.querySelector(".tab-content.active table");
  if (!table) return;

  let csv = "\uFEFF";
  const rows = table.querySelectorAll("tr");
  rows.forEach(r => {
    const cols = r.querySelectorAll("th, td");
    const rowData = [];
    cols.forEach(c => {
      let t = c.innerText.split(String.fromCharCode(10)).join(" ").split(";").join(",").trim();
      rowData.push(`"${t}"`);
    });
    if (rowData.length) csv += rowData.join(";") + String.fromCharCode(13, 10);
  });

  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `Evolucao_Carteira_NO_${appState.mes}_${appState.tipo}.csv`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

// Ordenação Genérica de Colunas (sortTable)
function sortTable(tableId, colIdx) {
  const tbl = document.getElementById(tableId);
  if (!tbl) return;
  const tbody = tbl.querySelector("tbody");
  if (!tbody) return;
  const rows = Array.from(tbody.querySelectorAll("tr"));

  const currentDir = tbl.getAttribute(`data-dir-${colIdx}`) || "asc";
  const newDir = currentDir === "asc" ? "desc" : "asc";
  tbl.setAttribute(`data-dir-${colIdx}`, newDir);

  rows.sort((a, b) => {
    const tdA = a.children[colIdx] ? a.children[colIdx].innerText.trim() : "";
    const tdB = b.children[colIdx] ? b.children[colIdx].innerText.trim() : "";

    const numA = parseFloat(tdA.split(".").join("").replace(",", ".").replace("%", ""));
    const numB = parseFloat(tdB.split(".").join("").replace(",", ".").replace("%", ""));

    if (!isNaN(numA) && !isNaN(numB)) {
      return newDir === "asc" ? numA - numB : numB - numA;
    }
    return newDir === "asc" ? tdA.localeCompare(tdB, "pt-BR") : tdB.localeCompare(tdA, "pt-BR");
  });

  rows.forEach(r => tbody.appendChild(r));
}

// Logout Seguro Corporativo
function executarLogout() {
  document.cookie = "pephub_session=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT; SameSite=Lax;";
  sessionStorage.clear();
  localStorage.clear();
  window.location.href = "/login/";
}

// Inicialização Principal ao Carregar o DOM
document.addEventListener("DOMContentLoaded", () => {
  popularSeletoresPeriodo();
  setupInteractiveFilters();
  sincronizarEstadoEUI();
  renderGlossario();

  if (typeof initPephubHeader === "function") {
    initPephubHeader("userWidget");
  }
});
</script>
</body>
</html>''')

with open(OUT_HTML, 'w', encoding='utf-8') as f:
    f.write(''.join(html_parts))

print(f"Página HTML regenerada com SUCESSO: {OUT_HTML}")
print(f"Tamanho do arquivo: {os.path.getsize(OUT_HTML):,} bytes")
