# -*- coding: utf-8 -*-
"""
Script de correção e padronização para relatorios/fpd_residencial/scripts/build.py
- Corrige SyntaxError gerado pelo escape de sortTable
- Remove qualquer resquício de parênteses no filtro Multi
- Padroniza o cabeçalho idêntico ao Churn Safra
- Padroniza os botões e abas idênticos ao Churn Safra
"""

import re
import os
import sys

try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

BUILD_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "relatorios", "fpd_residencial", "scripts", "build.py")

with open(BUILD_FILE, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Substituição do Header HTML
header_old_regex = re.compile(r'<header>.*?</header>', re.DOTALL)
header_new = """<header>
  <div class="hd-bar">
    <div class="hd-ico">
      <svg viewBox="0 0 48 48" width="34" height="34" aria-hidden="true">
        <circle cx="24" cy="24" r="21" fill="none" stroke="#fff" stroke-width="2.6"/>
        <path d="M31.5 16.5 L26.5 26.5 L16.5 31.5 L21.5 21.5 Z" fill="#fff"/>
      </svg>
    </div>
    <h1><b>FPD Residencial</b> <span>Regional Norte</span></h1>
    <div style="margin-left:auto;display:flex;align-items:center;gap:10px;flex-wrap:wrap">
      <a href="/fpd-residencial/download" download="Painel_FPD_Residencial_Regional_Norte.html" class="dl-btn" title="Baixar arquivo HTML independente com todos os dados para envio por e-mail">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;margin-right:6px"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
        Exportar para E-mail (.html)
      </a>
      <div id="fpdUserWidget" style="display:flex;align-items:center;gap:8px"></div>
    </div>
  </div>
  <div class="hd-sub">
    <a href="/" class="back-hub" title="Voltar ao Pephub — Portal de Churn & Qualidade">‹ Portal Pephub</a>
    <span class="dot"></span>
    <span><b>13 Safras</b> · jun/25 a jun/26</span>
    <span class="dot"></span>
    <span>Safra Foco: <b>Jun/26</b></span>
    <span class="dot"></span>
    <span>Bases: <b>BASE.xlsx</b> (Regional) e <b>BASE_BRASIL.xlsx</b> (Benchmark)</span>
    <div class="hd-right">
      <span>Métricas Oficiais: <b>FPD 60 Dias, FPD 30 Dias, Inadimplentes e Instalações</b></span>
    </div>
  </div>
</header>"""

if header_old_regex.search(content):
    content = header_old_regex.sub(header_new, content, count=1)
    print("✓ Header HTML padronizado com sucesso.")
else:
    print("! Header HTML não encontrado via regex.")

# 2. Navegação entre visões (Abas executivas superiores)
nav_old = """  <!-- NAVEGAÇÃO ENTRE VISÕES (ABAS EXECUTIVAS) -->
  <div class="tabs">
    <button class="on" onclick="switchView('tabCanal', this)">1. Visão por Canal de Venda</button>
    <button onclick="switchView('tabCidade', this)">2. Visão por Cidade / Praça</button>
    <button onclick="switchView('tabAA', this)">3. Agente Autorizado (AA)</button>
    <button onclick="switchView('tabPAP', this)">4. Porta a Porta (PAP)</button>
    <button onclick="switchView('tabVarejo', this)">5. Canal Varejo</button>
    <button onclick="switchView('tabLojas', this)">6. Lojas Próprias</button>
  </div>"""

nav_new = """  <!-- NAVEGAÇÃO ENTRE VISÕES (ABAS EXECUTIVAS) -->
  <div class="tabs view-tabs" style="margin-bottom:14px">
    <button class="on" onclick="switchView('tabCanal', this)">1. Visão por Canal de Venda</button>
    <button onclick="switchView('tabCidade', this)">2. Visão por Cidade / Praça</button>
    <button onclick="switchView('tabAA', this)">3. Agente Autorizado (AA)</button>
    <button onclick="switchView('tabPAP', this)">4. Porta a Porta (PAP)</button>
    <button onclick="switchView('tabVarejo', this)">5. Canal Varejo</button>
    <button onclick="switchView('tabLojas', this)">6. Lojas Próprias</button>
  </div>"""

if nav_old in content:
    content = content.replace(nav_old, nav_new)
    print("✓ Abas executivas atualizadas para .view-tabs.")

# 3. Substituição de metric-tabs por span.tabs e metric-btn por botões padrão
def replace_metric_tabs(text):
    # Encontrar cada bloco <div class="metric-tabs"...> ... </div>
    pattern = re.compile(r'<div class="metric-tabs"\s+data-table="([^"]+)">\s*(.*?)\s*</div>', re.DOTALL)

    def sub_fn(m):
        tbl = m.group(1)
        inner = m.group(2)
        # Substitui classes nos botões
        inner = re.sub(r'class="metric-btn\s+f60\s+active"', 'class="on"', inner)
        inner = re.sub(r'class="metric-btn[^"]*"', '', inner)
        # Limpar espaços duplos
        inner = re.sub(r'<button\s+', '<button ', inner)
        return f'<span class="tabs" data-table="{tbl}">\n              {inner.strip()}\n            </span>'

    new_text, count = pattern.subn(sub_fn, text)
    print(f"✓ Substituídos {count} blocos de metric-tabs por span.tabs padrão Churn Safra.")
    return new_text

content = replace_metric_tabs(content)

# 4. Atualização de switchView e setTableMetric no JS
old_switch = """function switchView(tabId, btn) {{
  document.querySelectorAll('.tabs button').forEach(b => b.classList.remove('on'));
  btn.classList.add('on');
  document.querySelectorAll('.view-pane').forEach(p => p.classList.remove('active'));
  document.getElementById(tabId).classList.add('active');
}}"""

new_switch = """function switchView(tabId, btn) {{
  document.querySelectorAll('.view-tabs button').forEach(b => b.classList.remove('on'));
  btn.classList.add('on');
  document.querySelectorAll('.view-pane').forEach(p => p.classList.remove('active'));
  const target = document.getElementById(tabId);
  if (target) target.classList.add('active');
}}"""

if old_switch in content:
    content = content.replace(old_switch, new_switch)
    print("✓ switchView atualizado.")

old_metric_fn = """function setTableMetric(tblId, metric, btn) {{
  tableMetrics[tblId] = metric;
  const container = btn.parentElement;
  container.querySelectorAll('.metric-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  renderSpecificTable(tblId);
}}"""

new_metric_fn = """function setTableMetric(tblId, metric, btn) {{
  tableMetrics[tblId] = metric;
  const container = btn.parentElement;
  container.querySelectorAll('button').forEach(b => b.classList.remove('on'));
  btn.classList.add('on');
  renderSpecificTable(tblId);
}}"""

if old_metric_fn in content:
    content = content.replace(old_metric_fn, new_metric_fn)
    print("✓ setTableMetric atualizado.")

# 5. Correção de renderTableHeader e sortTable
old_rth = """// Cabeçalho de Tabela Padronizado com Ordenação
function renderTableHeader(tblId, firstColName, isAllMetrics) {{
  const thead = document.querySelector(`#${{tblId}} thead`);
  const extraTh = isAllMetrics ? '<th class="l sortable" onclick="sortTable(this, \\'' + tblId + '\\', 1)">Indicador / Métrica <span class="sort-arrow">↕</span></th>' : '';
  const firstColIdx = 0;
  let colOffset = isAllMetrics ? 2 : 1;

  let hHtml = `<tr>
    <th class="l sortable" onclick="sortTable(this, '${{tblId}}', 0)">${{firstColName}} <span class="sort-arrow">↕</span></th>
    ${{extraTh}}
    <th class="th-foco sortable" onclick="sortTable(this, '${{tblId}}', ${{colOffset}})">JUN/26 (FOCO) <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, '${{tblId}}', ${{colOffset + 1}})">MAI/26 <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, '${{tblId}}', ${{colOffset + 2}})">DELTA MOM <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, '${{tblId}}', ${{colOffset + 3}})">DELTA YOY <span class="sort-arrow">↕</span></th>
    <th class="th-hist-start sortable" onclick="sortTable(this, '${{tblId}}', ${{colOffset + 4}})">JUN/25 <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, '${{tblId}}', ${{colOffset + 5}})">JUL/25 <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, '${{tblId}}', ${{colOffset + 6}})">AGO/25 <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, '${{tblId}}', ${{colOffset + 7}})">SET/25 <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, '${{tblId}}', ${{colOffset + 8}})">OUT/25 <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, '${{tblId}}', ${{colOffset + 9}})">NOV/25 <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, '${{tblId}}', ${{colOffset + 10}})">DEZ/25 <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, '${{tblId}}', ${{colOffset + 11}})">JAN/26 <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, '${{tblId}}', ${{colOffset + 12}})">FEV/26 <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, '${{tblId}}', ${{colOffset + 13}})">MAR/26 <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, '${{tblId}}', ${{colOffset + 14}})">ABR/26 <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, '${{tblId}}', ${{colOffset + 15}})">MAI/26 <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, '${{tblId}}', ${{colOffset + 16}})">JUN/26 <span class="sort-arrow">↕</span></th>
  </tr>`;
  thead.innerHTML = hHtml;
}}"""

new_rth = """// Cabeçalho de Tabela Padronizado com Ordenação
function renderTableHeader(tblId, firstColName, isAllMetrics) {{
  const thead = document.querySelector(`#${{tblId}} thead`);
  const extraTh = isAllMetrics ? '<th class="l sortable" onclick="sortTable(this, 1)">Indicador / Métrica <span class="sort-arrow">↕</span></th>' : '';
  let colOffset = isAllMetrics ? 2 : 1;

  let hHtml = `<tr>
    <th class="l sortable" onclick="sortTable(this, 0)">${{firstColName}} <span class="sort-arrow">↕</span></th>
    ${{extraTh}}
    <th class="th-foco sortable" onclick="sortTable(this, ${{colOffset}})">JUN/26 (FOCO) <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, ${{colOffset + 1}})">MAI/26 <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, ${{colOffset + 2}})">DELTA MOM <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, ${{colOffset + 3}})">DELTA YOY <span class="sort-arrow">↕</span></th>
    <th class="th-hist-start sortable" onclick="sortTable(this, ${{colOffset + 4}})">JUN/25 <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, ${{colOffset + 5}})">JUL/25 <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, ${{colOffset + 6}})">AGO/25 <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, ${{colOffset + 7}})">SET/25 <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, ${{colOffset + 8}})">OUT/25 <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, ${{colOffset + 9}})">NOV/25 <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, ${{colOffset + 10}})">DEZ/25 <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, ${{colOffset + 11}})">JAN/26 <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, ${{colOffset + 12}})">FEV/26 <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, ${{colOffset + 13}})">MAR/26 <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, ${{colOffset + 14}})">ABR/26 <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, ${{colOffset + 15}})">MAI/26 <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, ${{colOffset + 16}})">JUN/26 <span class="sort-arrow">↕</span></th>
  </tr>`;
  thead.innerHTML = hHtml;
}}"""

if old_rth in content:
    content = content.replace(old_rth, new_rth)
    print("✓ renderTableHeader corrigido com sucesso.")

# 6. Atualização de renderTableParceiroPresencial
old_rtp = """  thead.innerHTML = `<tr>
    <th class="l sortable" onclick="sortTable(this, '${{tblId}}', 0)">Parceiro Comercial <span class="sort-arrow">↕</span></th>
    <th class="l sortable" onclick="sortTable(this, '${{tblId}}', 1)">Praças Atendidas <span class="sort-arrow">↕</span></th>
    <th class="th-foco sortable" onclick="sortTable(this, '${{tblId}}', 2)">JUN/26 (FOCO) <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, '${{tblId}}', 3)">MAI/26 <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, '${{tblId}}', 4)">DELTA MOM <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, '${{tblId}}', 5)">DELTA YOY <span class="sort-arrow">↕</span></th>
    <th class="th-hist-start sortable" onclick="sortTable(this, '${{tblId}}', 6)">JUN/25 <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, '${{tblId}}', 7)">JUL/25 <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, '${{tblId}}', 8)">AGO/25 <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, '${{tblId}}', 9)">SET/25 <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, '${{tblId}}', 10)">OUT/25 <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, '${{tblId}}', 11)">NOV/25 <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, '${{tblId}}', 12)">DEZ/25 <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, '${{tblId}}', 13)">JAN/26 <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, '${{tblId}}', 14)">FEV/26 <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, '${{tblId}}', 15)">MAR/26 <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, '${{tblId}}', 16)">ABR/26 <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, '${{tblId}}', 17)">MAI/26 <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, '${{tblId}}', 18)">JUN/26 <span class="sort-arrow">↕</span></th>
  </tr>`;"""

new_rtp = """  thead.innerHTML = `<tr>
    <th class="l sortable" onclick="sortTable(this, 0)">Parceiro Comercial <span class="sort-arrow">↕</span></th>
    <th class="l sortable" onclick="sortTable(this, 1)">Praças Atendidas <span class="sort-arrow">↕</span></th>
    <th class="th-foco sortable" onclick="sortTable(this, 2)">JUN/26 (FOCO) <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, 3)">MAI/26 <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, 4)">DELTA MOM <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, 5)">DELTA YOY <span class="sort-arrow">↕</span></th>
    <th class="th-hist-start sortable" onclick="sortTable(this, 6)">JUN/25 <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, 7)">JUL/25 <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, 8)">AGO/25 <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, 9)">SET/25 <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, 10)">OUT/25 <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, 11)">NOV/25 <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, 12)">DEZ/25 <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, 13)">JAN/26 <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, 14)">FEV/26 <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, 15)">MAR/26 <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, 16)">ABR/26 <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, 17)">MAI/26 <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, 18)">JUN/26 <span class="sort-arrow">↕</span></th>
  </tr>`;"""

if old_rtp in content:
    content = content.replace(old_rtp, new_rtp)
    print("✓ renderTableParceiroPresencial corrigido com sucesso.")

# 7. Atualização da assinatura de sortTable
old_sort_fn_head = """function sortTable(thEl, tblId, colIdx) {{
  const table = document.getElementById(tblId);"""

new_sort_fn_head = """function sortTable(thEl, colIdx) {{
  const table = thEl.closest('table');
  if (!table) return;
  const tblId = table.id;"""

if old_sort_fn_head in content:
    content = content.replace(old_sort_fn_head, new_sort_fn_head)
    print("✓ sortTable atualizado para obter table dinamicamente.")

# 8. Botões dos filtros (fbar)
old_fbar = """      <div class="fbar">
        <button class="btn-apply" onclick="applyFilters()">Aplicar Filtros</button>
        <button class="btn-clear" onclick="resetFilters()">Limpar Todos</button>
        <div class="chips" id="activeFilterChips"></div>
      </div>"""

new_fbar = """      <div class="fbar">
        <button class="primary" id="btnApply" onclick="applyFilters()">Aplicar Filtros</button>
        <button id="btnClear" onclick="resetFilters()">Limpar Todos</button>
        <div class="chips" id="activeFilterChips"></div>
      </div>"""

if old_fbar in content:
    content = content.replace(old_fbar, new_fbar)
    print("✓ fbar botões padronizados.")

with open(BUILD_FILE, "w", encoding="utf-8") as f:
    f.write(content)

print("Patch aplicado no build.py.")
