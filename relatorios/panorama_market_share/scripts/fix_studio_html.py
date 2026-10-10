import re

with open('public_staging/pep-tools/market-share/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update .panel CSS
old_panel_css = """.panel { background: var(--panel); border: 1px solid var(--line); border-radius: 3px; margin-bottom: 14px; }"""
new_panel_css = """.panel { display: none; background: var(--panel); border: 1px solid var(--line); border-radius: 3px; margin-bottom: 14px; }
.panel.active { display: grid !important; grid-template-columns: 410px 1fr; gap: 20px; align-items: start; }
.panel.wide.active { grid-template-columns: 1fr !important; }
@media(max-width:940px) { .panel.active { grid-template-columns: 1fr !important; } }
.card { background: #fff; border: 1px solid var(--line); border-radius: 3px; padding: 18px 20px; box-shadow: none; margin-bottom: 14px; }
.card-label { font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: .6px; color: var(--ink2); margin-bottom: 14px; display: flex; align-items: center; gap: 8px; border-bottom: 1px solid var(--line2); padding-bottom: 8px; }
.preview-card { background: #fff; border: 1px solid var(--line); border-radius: 3px; box-shadow: none; overflow: hidden; position: sticky; top: 20px; }
.preview-head { display: flex; align-items: center; justify-content: space-between; padding: 10px 14px; border-bottom: 1px solid var(--line2); background: #f7f8fa; }
.preview-head h3 { font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: .4px; color: var(--ink2); margin: 0; }
"""
if old_panel_css in html:
    html = html.replace(old_panel_css, new_panel_css, 1)
    print("Panel CSS updated.")
else:
    print("Warning: old_panel_css not found!")

# 2. Add autoColorToggle in header actions
old_actions = """    <div style="margin-left:auto; display:flex; align-items:center; gap:8px;">
      <button class="hlp" data-h="scatter" style="display:none">?</button>
      <button class="hlp" data-h="risco" style="display:none">?</button>
      <button class="hlp" data-h="studio" title="Ajuda">?</button>
      <a href="/" class="back-hub">‹ Portal Pephub</a>
    </div>"""

new_actions = """    <div style="margin-left:auto; display:flex; align-items:center; gap:12px;">
      <label style="display:inline-flex; align-items:center; gap:6px; font-size:11.5px; color:#fff; cursor:pointer;">
        <input type="checkbox" id="autoColorToggle" checked onchange="onAutoToggle()" style="accent-color:var(--gold);">
        <span>Cor Automática</span>
      </label>
      <button class="hlp" data-h="studio" title="Ajuda">?</button>
      <a href="/" class="back-hub">‹ Portal Pephub</a>
    </div>"""

if old_actions in html:
    html = html.replace(old_actions, new_actions, 1)
    print("Header actions with autoColorToggle updated.")
else:
    print("Warning: old_actions not found!")

# 3. Clean tabs without emojis
tabs_pattern = r'<div class="tabs">.*?</div>\s*<style id="tfStyle">'
new_tabs = """<div class="tabs">
  <button class="tab" data-tab="data" onclick="switchTab('data')">Base &amp; Filtros</button>
  <button class="tab active on" data-tab="share" onclick="switchTab('share')">Market Share</button>
  <button class="tab" data-tab="donut" onclick="switchTab('donut')">Rosca / Pizza</button>
  <button class="tab" data-tab="ranking" onclick="switchTab('ranking')">Ranking</button>
  <button class="tab" data-tab="columns" onclick="switchTab('columns')">Colunas</button>
  <button class="tab" data-tab="funnel" onclick="switchTab('funnel')">Funil</button>
  <button class="tab" data-tab="tree" onclick="switchTab('tree')">Treemap</button>
  <button class="tab" data-tab="bubbles" onclick="switchTab('bubbles')">Bolhas</button>
  <button class="tab" data-tab="radar" onclick="switchTab('radar')">Radar</button>
  <button class="tab" data-tab="history" onclick="switchTab('history')">Histórico</button>
  <button class="tab" data-tab="sankey" onclick="switchTab('sankey')">Sankey</button>
  <button class="tab" data-tab="info" onclick="switchTab('info')">Infográfico</button>
  <button class="tab" data-tab="org" onclick="switchTab('org')">Organograma</button>
  <button class="tab" data-tab="table" onclick="switchTab('table')">Tabela</button>
  <button class="tab" data-tab="compare" onclick="switchTab('compare')">Comparativos</button>
  <button class="tab" data-tab="batch" onclick="switchTab('batch')">Lote</button>
  <button class="tab" data-tab="pill" onclick="switchTab('pill')">Pílulas</button>
  <button class="tab" data-tab="labels" onclick="switchTab('labels')">Rótulos</button>
</div>
<style id="tfStyle">"""

html = re.sub(tabs_pattern, new_tabs, html, count=1, flags=re.DOTALL)
print("Tabs updated without emojis.")

# 4. Clean bottom scripts (remove duplicate HELP declarations and hanging divs)
# Find everything after the main script init
init_line = "storageWarn();\n\n</script>"
if init_line in html:
    idx = html.find(init_line) + len(init_line)
    bottom_clean = """

<script>
window.HELP = {
  studio: "Gerador vetorial de gráficos de Market Share (Pizza, Rosca, Barras, Histórico) 100% alinhados à identidade Claro.",
  scatter: "Visualização de dispersão de share e volume entre concorrentes.",
  risco: "Análise de distribuição e concentração de base."
};
document.addEventListener('click', function(e) {
  if (e.target && e.target.classList && e.target.classList.contains('hlp')) {
    const key = e.target.getAttribute('data-h');
    if (window.HELP && window.HELP[key]) alert(window.HELP[key]);
  }
});
</script>
</div> <!-- fim .wrap -->
</body>
</html>
"""
    html = html[:idx] + bottom_clean
    print("Bottom scripts cleaned up successfully.")
else:
    print("Warning: init_line not found!")

# 5. Clean emojis from card labels and tooltips in HTML
emoji_replacements = [
    ("⚙️ 2. Filtros", "2. Filtros"),
    ("🎛️ 1. Configurações", "1. Configurações"),
    ("🎛️ Ajuste p/ exportar:", "Ajuste para Exportar:"),
    ("🎨 Cores recentes:", "Cores Recentes:"),
    ("⭐ Cores salvas:", "Cores Salvas:"),
    ("💾 Backup", "Backup"),
    ("📂 Restaurar", "Restaurar"),
    ("🧩 Modelos de gráfico:", "Modelos de Gráfico:"),
    ("📦 Salvar tudo", "Salvar Tudo"),
    ("🎨 Salvar só layout", "Salvar Só Layout"),
    ("⚠️ Leitor", "Aviso: Leitor"),
    ("⚠️ Este navegador", "Aviso: Este navegador"),
    ("️ 1. Carregar base", "1. Carregar Base"),
    ("⚡ Exportar Todos", "Exportar Todos"),
    ("📋 Copiar", "Copiar"),
]
for old_e, new_e in emoji_replacements:
    html = html.replace(old_e, new_e)

with open('public_staging/pep-tools/market-share/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Saved updated public_staging/pep-tools/market-share/index.html")
