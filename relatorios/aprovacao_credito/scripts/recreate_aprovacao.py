import re

# Read from pristine original source file
with open('Painel Aprovacao Credito RNO 2.4.html', 'r', encoding='utf-8') as f:
    orig_content = f.read()

# Extract script blocks
scripts = re.findall(r'<script[^>]*>(.*?)</script>', orig_content, re.DOTALL)
if len(scripts) < 3:
    raise ValueError(f"Expected 3 script blocks in Painel Aprovacao Credito RNO 2.4.html, found {len(scripts)}")

# Script 0 is empty, Script 1 is DASH_DATA, Script 2 is engine
data_script = scripts[1]
engine_script = scripts[2]

# 1. Clean emojis and informal icons in engine_script
emoji_replacements = [
    ("\U0001f50e Buscar por Nome Fantasia, DV_", "Buscar por Nome Fantasia, DV_"),
    ("\U0001f50e Buscar canal ou parceiro", "Buscar canal ou parceiro"),
    ("\U0001f50e Buscar equipe de venda", "Buscar equipe de venda"),
    ("\U0001f50e", ""),
    ("\U0001f4c1 Escolher arquivo (.csv recomendado)", "Escolher arquivo (.csv recomendado)"),
    ("\U0001f4c1 Escolher arquivo (.xlsx)", "Escolher arquivo (.xlsx)"),
    ("\U0001f4c1 Escolher arquivo", "Escolher arquivo"),
    ("\U0001f4c1", ""),
    ("\U0001f5a8\ufe0f Imprimir / PDF", "Imprimir / PDF"),
    ("\U0001f5a8", ""),
    ("\U0001f3f7\ufe0f Top 5", "Top 5"),
    ("\U0001f3f7", ""),
    ("\U0001f4c8 Linhas", "Linhas"),
    ("\U0001f4c8", ""),
    ("\U0001f50d Ampliar", "Ampliar"),
    ("\U0001f50d", ""),
    ("\U0001f4a1 PDVs acima da linha", "PDVs acima da linha"),
    ("\U0001f4a1", ""),
    ("\U0001f4cc <b>Síntese:</b>", "<b>Síntese:</b>"),
    ("\U0001f4cc <b>Base grande", "<b>Base grande"),
    ("\U0001f4cc", ""),
    ("\U0001f511 <b>Cascata de carteirização:", "<b>Cascata de carteirização:"),
    ("\U0001f511", ""),
    ("⚠️ Ferramenta em testes", "[Piloto] Ferramenta em testes"),
    ("⚠️ A biblioteca de leitura de Excel", "A biblioteca de leitura de Excel"),
    ("⚠️", ""),
    ("➕", "+"),
]
for old_s, new_s in emoji_replacements:
    engine_script = engine_script.replace(old_s, new_s)

# 2. Update go(v) to toggle both .active and .on classes on .tabs a
engine_script = re.sub(
    r"document\.querySelectorAll\('#nav a'\)\.forEach\(a=>a\.classList\.toggle\('active',a\.dataset\.v===v\)\);",
    "document.querySelectorAll('#nav a').forEach(a=>{a.classList.toggle('active',a.dataset.v===v); a.classList.toggle('on',a.dataset.v===v);});",
    engine_script
)

# 3. Update render() to safely set ttl and tsub and update note
old_render_head = "document.getElementById('ttl').childNodes[0].nodeValue=TITLES[S.view][0];"
new_render_head = """const ttlEl = document.getElementById('ttl');
  if (ttlEl && ttlEl.childNodes.length > 0) ttlEl.childNodes[0].nodeValue = TITLES[S.view][0];
  const tsubEl = document.getElementById('tsub');
  if (tsubEl) tsubEl.textContent = TITLES[S.view][1];
  const vNote = document.getElementById('viewNote');
  if (vNote) vNote.textContent = TITLES[S.view][1] || '';"""
engine_script = engine_script.replace(old_render_head, new_render_head)

# 4. Extract and clean component CSS from original file
pos_s = orig_content.find('<style>')
pos_e = orig_content.find('</style>')
orig_css = orig_content[pos_s+7:pos_e]

# Remove legacy sidebar #side, #app, #main, .brand, .navi layout rules
component_css = orig_css
component_css = re.sub(r'#app\b[^{]*\{[^}]*\}', '', component_css)
component_css = re.sub(r'#side\b[^{]*\{[^}]*\}', '', component_css)
component_css = re.sub(r'#main\b[^{]*\{[^}]*\}', '', component_css)
component_css = re.sub(r'\.brand\b[^{]*\{[^}]*\}', '', component_css)
component_css = re.sub(r'\.navi\b[^{]*\{[^}]*\}', '', component_css)
component_css = re.sub(r'\.sidetoggle\b[^{]*\{[^}]*\}', '', component_css)
component_css = re.sub(r'\.topbar\b[^{]*\{[^}]*\}', '', component_css)
component_css = re.sub(r'body\.side-collapsed[^{]*\{[^}]*\}', '', component_css)

# Replace dark hero / cover gradients with clean white panels
component_css = re.sub(
    r'\.cover-hero\s*\{[^}]*\}',
    '.cover-hero{background:#fff;border:1px solid var(--line);border-radius:3px;padding:22px;margin-bottom:14px;color:var(--ink);box-shadow:none}',
    component_css
)
component_css = re.sub(
    r'\.chero\s*\{[^}]*\}',
    '.chero{background:#fff;border:1px solid var(--line);border-radius:3px;padding:16px;margin-bottom:14px;color:var(--ink);box-shadow:none}',
    component_css
)
component_css = re.sub(
    r'\.chero\s+h2[^{]*\{[^}]*\}',
    '.chero h2{color:var(--ink) !important;font-size:20px;font-weight:700;margin-bottom:6px}',
    component_css
)
component_css = re.sub(
    r'\.chero\s+\.lead[^{]*\{[^}]*\}',
    '.chero .lead{color:var(--ink2) !important;font-size:12px;margin-bottom:10px}',
    component_css
)
component_css = re.sub(
    r'\.chero\s+\.fignum[^{]*\{[^}]*\}',
    '.chero .fignum{color:var(--ink) !important;font-size:30px !important}',
    component_css
)
component_css = re.sub(
    r'\.chero\s+\.figlab[^{]*\{[^}]*\}',
    '.chero .figlab{color:var(--ink3) !important;font-size:11px}',
    component_css
)
component_css = re.sub(
    r'\.chero\s+\.fchip[^{]*\{[^}]*\}',
    '.chero .fchip{font-size:11px;font-weight:700;padding:2px 8px;border-radius:2px;background:#f0f2f5;color:var(--ink2);border:1px solid var(--line)}',
    component_css
)
component_css = re.sub(
    r'\.cta-bar\s*\{[^}]*\}',
    '.cta-bar{background:#f7f8fa;border:1px solid var(--line);border-radius:3px;padding:12px 16px;margin-bottom:14px;display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;box-shadow:none}',
    component_css
)
component_css = re.sub(
    r'\.cta-bar\s+\.txt\s+h4[^{]*\{[^}]*\}',
    '.cta-bar .txt h4{color:var(--ink) !important;font-size:13px;font-weight:700;margin:0 0 2px}',
    component_css
)
component_css = re.sub(
    r'\.cta-bar\s+\.txt\s+p[^{]*\{[^}]*\}',
    '.cta-bar .txt p{color:var(--ink2) !important;font-size:11.5px;margin:0}',
    component_css
)
component_css = re.sub(
    r'\.cta-bar\s+\.goact[^{]*\{[^}]*\}',
    '.cta-bar .goact{background:var(--nav) !important;color:#fff !important;border-radius:2px;padding:6px 14px;font-size:11.5px;font-weight:600;text-decoration:none;display:inline-flex;align-items:center;gap:6px}',
    component_css
)
component_css = re.sub(
    r'\.ob-head\s*\{[^}]*\}',
    '.ob-head{background:var(--nav);color:#fff;padding:16px 20px;border-radius:3px 3px 0 0}',
    component_css
)
component_css = re.sub(
    r'\.ob-head\s+\.tag[^{]*\{[^}]*\}',
    '.ob-head .tag{display:inline-block;font-size:10px;font-weight:800;letter-spacing:1px;text-transform:uppercase;background:var(--warn);color:#8a6400;padding:2px 8px;border-radius:2px;margin-bottom:6px}',
    component_css
)
component_css = re.sub(
    r'\.hlcard\s*\{[^}]*\}',
    '.hlcard{background:#fff;border:1px solid var(--line);border-radius:3px;padding:12px 14px;box-shadow:none}',
    component_css
)

# Convert bubble border radius (12px, 14px, 16px, 18px, 20px, 999px) to 2px/3px
component_css = re.sub(r'border-radius:\s*(?:12|14|16|18|20)px', 'border-radius:3px', component_css)
component_css = re.sub(r'border-radius:\s*999px', 'border-radius:2px', component_css)

base_css = """
:root {
  --bg: #f4f5f7;
  --panel: #ffffff;
  --card: #ffffff;
  --ink: #1c2430;
  --ink2: #5b6675;
  --ink3: #8b95a3;
  --line: #dfe3e8;
  --line2: #eceef1;
  --nav: #1b2430;
  --nav2: #27323f;
  --red: #c0392b;
  --amber: #c98a15;
  --green: #2f7d5d;
  --blue: #2a5d8f;
  --purple: #6b4b8a;
  --claro: #c0392b;
  --claro-d: #8a0f18;
  --navy: #1b2430;
  --navy2: #27323f;
  --muted: #5b6675;
  --good: #eaf2ec;
  --warn: #fdf3e2;
  --bad: #fdece9;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--ink);
  font: 13px/1.45 "Segoe UI", Roboto, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
}

/* Header Corporativo Oficial Claro PEP HUB */
header { background: #fff; }
.hd-bar {
  background: linear-gradient(90deg, #8a0f18 0%, #c0191f 26%, #e23a1e 50%, #f47a1f 74%, #f9b233 100%);
  display: flex; align-items: center; gap: 16px; padding: 14px 26px; flex-wrap: wrap;
}
.hd-ico {
  width: 44px; height: 44px; min-width: 44px; border-radius: 50%;
  border: 2.4px solid rgba(255,255,255,.95); display: flex; align-items: center; justify-content: center;
}
.hd-bar h1 {
  margin: 0; color: #fff; font-size: 26px; font-weight: 400; letter-spacing: -.4px; line-height: 1.1;
  display: flex; align-items: baseline; gap: 10px; flex-wrap: wrap;
}
.hd-bar h1 b { font-weight: 800; letter-spacing: -0.5px; }
.hd-bar h1 span { font-weight: 300; font-size: 20px; color: rgba(255,255,255,.92); }

/* Botoes de Acao Superior Direito (Padrao FPD / Safra / Panorama) */
.hd-actions { margin-left: auto; display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.hd-btn {
  background: rgba(255,255,255,.22) !important; color: #ffffff !important; border: 1px solid rgba(255,255,255,.55) !important;
  padding: 6px 14px !important; border-radius: 4px !important; font-size: 11.5px !important; font-weight: 700 !important;
  text-decoration: none !important; transition: all .15s ease !important; cursor: pointer !important;
  display: inline-flex !important; align-items: center !important; gap: 6px !important; white-space: nowrap !important;
  box-shadow: 0 1px 3px rgba(0,0,0,.18) !important;
}
.hd-btn:hover { background: rgba(255,255,255,.38) !important; color: #ffffff !important; border-color: #ffffff !important; }

/* Subheader com Breadcrumb e Contexto */
.hd-sub {
  background: var(--nav); color: #aab4c0; font-size: 11.5px; padding: 7px 26px;
  display: flex; align-items: center; gap: 10px; flex-wrap: wrap;
}
.hd-sub b { color: #e8edf3; font-weight: 600; }
.hd-sub .dot { width: 3px; height: 3px; border-radius: 50%; background: #5b6675; display: inline-block; }
.hd-sub .hd-right { margin-left: auto; display: flex; align-items: center; gap: 8px; color: #8b95a3; font-weight: 600; }
.hd-sub a, .hd-sub .back-hub { color: #f9b233 !important; text-decoration: none !important; font-weight: 700 !important; display: inline-flex; align-items: center; gap: 4px; }
.hd-sub a:hover, .hd-sub .back-hub:hover { color: #ffffff !important; text-decoration: underline !important; }

/* Conteiner Geral */
.wrap { padding: 16px 26px 40px; max-width: 2400px; margin: 0 auto; }

/* Paineis Analiticos (Churn Safra Standard) */
.panel { background: var(--panel); border: 1px solid var(--line); border-radius: 3px; margin-bottom: 14px; }
.panel > h2 {
  margin: 0; padding: 10px 14px; font-size: 12px; font-weight: 600; text-transform: uppercase;
  letter-spacing: .6px; color: var(--ink2); border-bottom: 1px solid var(--line2);
  display: flex; align-items: center; gap: 10px; flex-wrap: wrap;
}
.panel > h2 .note { text-transform: none; letter-spacing: 0; font-weight: 400; color: var(--ink3); font-size: 11px; }
.pbody { padding: 14px; }

/* Gaveta de Filtros Retratil (.drawer-btn) */
.drawer-btn {
  display: inline-flex; align-items: center; gap: 6px; background: var(--nav); color: #fff;
  border: 1px solid var(--line); border-radius: 2px; padding: 4px 10px; font-size: 11px;
  font-weight: 600; cursor: pointer; transition: background .15s;
}
.drawer-btn:hover { background: var(--nav2); }
.drawer-btn span { font-size: 9px; transition: transform .15s; display: inline-block; }
.drawer-btn.open span { transform: rotate(90deg); }

/* Botao CSV */
.btn-csv {
  display: inline-flex; align-items: center; gap: 5px;
  background: #fff; color: var(--ink2); border: 1px solid var(--line);
  padding: 3px 9px; border-radius: 2px; font-size: 11px; font-weight: 600;
  cursor: pointer; transition: all .15s;
}
.btn-csv:hover { background: #f0f2f5; color: var(--nav); border-color: var(--nav); }

/* Botao Help Modal */
.hlp {
  margin-left: auto; width: 19px; height: 19px; min-width: 19px; border-radius: 50%;
  border: 1px solid var(--line); background: #fff; color: var(--ink3);
  font: 600 11px "Segoe UI", Arial; line-height: 1; cursor: pointer;
  display: inline-flex; align-items: center; justify-content: center; padding: 0; flex: none;
}
.hlp:hover { background: var(--nav); color: #fff; border-color: var(--nav); }

/* Abas de Navegacao (.tabs a.on e .tabs a.active) */
.tabs { display: flex; gap: 4px; flex-wrap: wrap; align-items: center; }
.tabs a, .tabs button {
  border: 1px solid var(--line); background: #fff; color: var(--ink);
  font-size: 11.5px; padding: 5px 12px; border-radius: 2px; text-decoration: none;
  font-weight: 600; cursor: pointer; transition: all .15s ease; display: inline-flex; align-items: center;
}
.tabs a:hover, .tabs button:hover { background: #f0f2f5; color: var(--nav); border-color: var(--nav); }
.tabs a.on, .tabs a.active, .tabs button.on, .tabs button.active {
  background: var(--nav) !important; color: #fff !important; border-color: var(--nav) !important;
}

/* Indicadores KPIs (Churn Safra Standard) */
.kpis {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(148px, 1fr));
  border: 1px solid var(--line2); background: #fff; border-radius: 3px; margin-bottom: 14px;
}
.kpi { padding: 10px 14px; border-right: 1px solid var(--line2); border-bottom: 1px solid var(--line2); background: #fff; }
.kpi:last-child { border-right: none; }
.kpi .k, .kpi .lab { font-size: 10.5px; text-transform: uppercase; letter-spacing: .5px; color: var(--ink3); font-weight: 600; display: block; }
.kpi .v, .kpi .val, .lvlcount .lc-num { font-size: 22px !important; font-weight: 600; margin-top: 3px; letter-spacing: -.3px; color: var(--ink); display: block; line-height: 1.1; }
.kpi .d, .kpi .sub, .kpi .dl { font-size: 11px; color: var(--ink2); margin-top: 2px; font-style: normal; display: block; }
.up { color: var(--green) !important; }
.down { color: var(--red) !important; }
.mut { color: var(--ink3) !important; }

/* Toggle */
.toggle { display: inline-flex; border: 1px solid var(--line); border-radius: 2px; overflow: hidden; background: #fff; height: 28px; }
.toggle button {
  border: none; border-right: 1px solid var(--line2); background: #fff; color: var(--ink2);
  padding: 0 11px; font: 600 11.5px "Segoe UI", Arial, sans-serif; cursor: pointer; line-height: 26px;
}
.toggle button:last-child { border-right: none; }
.toggle button:hover { background: #f0f2f5; color: var(--ink); }
.toggle button.on { background: var(--nav) !important; color: #fff !important; font-weight: 700; }

/* Tabelas Analiticas */
.tablewrap, .dualscroll .ds-body { overflow-x: auto; border: 1px solid var(--line2); border-radius: 3px; background: #fff; margin-top: 8px; }
table { width: 100%; border-collapse: collapse; font-size: 12px; }
th, td { padding: 6px 8px; border-bottom: 1px solid var(--line2); text-align: right; white-space: nowrap; }
th {
  background: #f7f8fa; color: var(--ink2); font-weight: 600; font-size: 10.5px;
  text-transform: uppercase; letter-spacing: .3px; position: sticky; top: 0; z-index: 2; border-bottom: 1px solid var(--line);
}
th:first-child, td:first-child { text-align: left; }
tbody tr:hover { background: #f7f9fb; }

/* Cards & Badges */
.card { background: #fff; border: 1px solid var(--line); border-radius: 3px; padding: 14px; margin-bottom: 14px; }
.card h3 { font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: .5px; color: var(--ink2); margin-bottom: 4px; }
.card .csub { font-size: 11px; color: var(--ink3); margin-bottom: 12px; }

.cbadge.ci { background: #eaf2ec; color: var(--green); }
.cbadge.cs { background: #eef2f6; color: var(--blue); }
.cbadge.ce { background: #fdf3e2; color: var(--amber); }

footer {
  border-top: 1px solid var(--line2); padding: 24px 0 10px; font-size: 11.5px; color: var(--ink3);
  margin-top: 24px; text-align: center; line-height: 1.6;
}
footer b { color: var(--ink2); }
"""

combined_css = base_css + "\n/* === Component CSS from Source === */\n" + component_css

html_body = """
<!-- Header Corporativo Oficial Claro PEP HUB -->
<header>
  <div class="hd-bar">
    <div class="hd-ico">
      <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
      </svg>
    </div>
    <h1>
      <b>Taxa de Aprovação de Crédito PF</b>
      <span>Cidade e PDV · Regional Norte</span>
    </h1>
    <div class="hd-actions">
      <a href="/" class="hd-btn" title="Voltar ao Pephub — Portal de Churn & Qualidade">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
        Portal Pephub
      </a>
      <a href="/churn/" class="hd-btn" title="Acessar o Painel de Churn Safra">Painel Safra</a>
      <a href="/fpd/" class="hd-btn" title="Acessar o Painel Executivo FPD">Painel FPD</a>
      <a href="/panorama-market-share/" class="hd-btn" title="Acessar o Panorama Market Share">Panorama MS</a>
      <a href="/pep-tools/market-share/" class="hd-btn" title="Acessar o Market Share Studio">MS Studio</a>
      <div id="userWidget" style="display:flex;align-items:center;gap:8px"></div>
    </div>
  </div>
  <div class="hd-sub">
    <a href="/" class="back-hub" title="Voltar ao Pephub — Portal de Churn & Qualidade">‹ Portal Pephub</a>
    <span class="dot"></span>
    <span>Posição Oficial: <b>Agosto / 2026</b></span>
    <span class="dot"></span>
    <span>Regional Norte <b>(AM · AP · MA · PA · PI · RR)</b></span>
    <span class="dot"></span>
    <span>Escopo: <b>Cidades e Redes de PDVs Residencial</b></span>
    <div class="hd-right"><span>Planejamento & Performance · Regional Norte</span></div>
  </div>
</header>

<div class="wrap">

  <!-- Painel de Navegação Executiva (Tabs Churn Safra com Controles) -->
  <div class="panel" style="margin-bottom:14px;">
    <h2>
      NAVEGAÇÃO DO PAINEL
      <span class="note" id="viewNote">Aberturas analíticas de aprovação, canais, PDVs e risco de inadimplência</span>
      <div style="margin-left:auto; display:flex; align-items:center; gap:10px;">
        <button class="drawer-btn" id="btnDrawer" onclick="toggleFilterDrawer()"><span id="drawerIco">▸</span> Filtros</button>
        <button class="btn-csv" onclick="exportActiveTableToCSV()">Exportar CSV</button>
        <div class="toggle" id="modeToggle" style="display:none">
          <button data-m="abs">Absoluto (Volume)</button>
          <button data-m="pct" class="on">Percentual (Taxa)</button>
        </div>
        <button class="hlp" data-h="scatter" title="Visão de Dispersão e Quadrantes">?</button>
        <button class="hlp" data-h="risco" title="Visão de Risco e Score">?</button>
      </div>
    </h2>
    <div class="pbody" style="padding:10px 14px;">
      <nav class="tabs" id="nav">
        <a data-v="capa" class="active on">Capa & Direcionamento</a>
        <a data-v="v1">1. Visão Geral</a>
        <a data-v="v2">2. Canais & PDVs</a>
        <a data-v="v3">3. Visão Diária</a>
        <a data-v="v4">4. PDVs Detalhados</a>
        <a data-v="cart">5. Carteira / Hierarquia</a>
        <a data-v="v5">6. Insights & Recomendações</a>
        <a data-v="sum">Resumo Geral</a>
        <a data-v="imp">Importar Dados</a>
      </nav>
      <div style="margin-top:10px; display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; border-top:1px solid var(--line2); padding-top:8px;">
        <h3 id="ttl" style="margin:0; font-size:14px; font-weight:700; color:var(--ink); display:flex; align-items:baseline; gap:8px;">
          Capa & Direcionamento
          <small id="tsub" style="font-size:11.5px; font-weight:400; color:var(--ink3);">Principais achados e navegação</small>
        </h3>
      </div>
    </div>
  </div>

  <!-- Conteúdo Dinâmico das Visões -->
  <div id="content"></div>

  <footer>
    <b>Painel Executivo de Taxa de Aprovação de Crédito PF — Banda Larga Residencial · Regional Norte</b><br>
    Posição Oficial: Agosto / 2026 · Elaborado pela equipe de Planejamento & Performance RNO.<br>
    Documento analítico executivo para uso corporativo exclusivo Claro Brasil.
  </footer>

</div>
"""

help_script = """
const HELP = {
  risco: "Visão de Risco & Score: Limiares de aprovação de entrada, ofensores de crédito (política interna), restrições externas (Serasa/SPC) e antifraude.",
  scatter: "Matriz de Dispersão & Quadrantes Estratégicos: Cruzamento entre taxa de aprovação e índices de risco e fraude por canal e cidade.",
  filtros: "Filtros multidimensionais que restringem a base por Safra, Cidade (CIDLAB), Segmento, Canal e Produto.",
  aprovacao: "Taxa de Aprovação = Propostas Aprovadas / Propostas Submetidas. Percentual de entrada de novos clientes residenciais.",
  canais: "Desempenho por Canal de Venda (Lojas Próprias, Agentes Autorizados, Televendas, Canais Digitais e Porta a Porta).",
  diaria: "Evolução temporal diária das taxas de aprovação e volume de propostas ao longo da safra corrente.",
  pdvs: "Ranking detalhado por DV_EQUIPE_VENDA e PDVs parceiros identificando ofensores de aprovação e fraude.",
  carteira: "Visão hierárquica por estrutura comercial: Canal > Gerência Regional > Gerência de Filial > Coordenação > Executivo.",
  insights: "Matriz de dispersão e quadrantes estratégicos cruzando taxa de aprovação com índice de recusa por fraude e inadimplência.",
  resumo: "Síntese executiva formatada para impressão gerencial e prestação de contas à diretoria regional."
};

document.addEventListener('click', function(e) {
  if (e.target && e.target.classList && e.target.classList.contains('hlp')) {
    const key = e.target.getAttribute('data-h');
    if (HELP[key]) alert(HELP[key]);
  }
});

// Gaveta de Filtros Retratil
function toggleFilterDrawer() {
  const f = document.querySelector('.filters');
  const btn = document.getElementById('btnDrawer');
  if (!f) return;
  if (f.style.display === 'none') {
    f.style.display = 'flex';
    if (btn) btn.classList.add('open');
  } else {
    f.style.display = 'none';
    if (btn) btn.classList.remove('open');
  }
}

// Exportacao CSV no Cliente (Blob / createObjectURL)
function exportActiveTableToCSV() {
  const table = document.querySelector('#content table');
  if (!table) {
    alert('Nenhuma tabela visível para exportação na visão atual.');
    return;
  }
  let csv = [];
  const rows = table.querySelectorAll('tr');
  for (let i = 0; i < rows.length; i++) {
    let row = [], cols = rows[i].querySelectorAll('th, td');
    for (let j = 0; j < cols.length; j++) {
      let data = cols[j].innerText.replace(/(\\r\\n|\\n|\\r)/gm, ' ').replace(/\"/g, '\"\"').trim();
      row.push('\"' + data + '\"');
    }
    csv.push(row.join(';'));
  }
  const blob = new Blob(['\\ufeff' + csv.join('\\r\\n')], { type: 'text/csv;charset=utf-8;' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `aprovacao_credito_${S ? S.view : 'dados'}.csv`;
  a.click();
}

// Autenticacao e Identidade do Usuario no Header
async function initUserWidget() {
  try {
    const res = await fetch('/api/auth/me');
    if (res.ok) {
      const u = await res.json();
      const el = document.getElementById('userWidget');
      if (el && u.authenticated) {
        const fn = u.nome_completo ? u.nome_completo.split(' ')[0] : 'Usuário';
        el.innerHTML = `
          <span style="color:#fff;font-size:11.5px;font-weight:600;white-space:nowrap;background:rgba(255,255,255,.15);padding:4px 8px;border-radius:3px">${fn} (${u.area || 'RNO'})</span>
          ${u.is_admin ? '<a href="/admin/" style="background:rgba(255,255,255,.2);color:#fff;border:1px solid rgba(255,255,255,.4);padding:4px 8px;border-radius:3px;font-size:10.5px;font-weight:700;text-decoration:none">Admin</a>' : ''}
          <button id="btnLogoutAprovacao" style="background:none;border:1px solid rgba(255,255,255,.3);color:#fff;padding:4px 8px;border-radius:3px;font-size:10.5px;cursor:pointer;font-weight:600">Sair</button>
        `;
        const btnLogout = document.getElementById('btnLogoutAprovacao');
        if (btnLogout) {
          btnLogout.addEventListener('click', async () => {
            await fetch('/api/auth/logout', { method: 'POST' });
            window.location.href = '/login/';
          });
        }
      }
    }
  } catch (e) {}
}
initUserWidget();
"""

full_html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Taxa de Aprovação de Crédito PF — Cidade e PDV · Regional Norte</title>
<style>{combined_css}</style>
</head>
<body>
{html_body}
<script>{data_script}</script>
<script>{engine_script}</script>
<script>{help_script}</script>
</body>
</html>
"""

with open('public_staging/aprovacao-credito/index.html', 'w', encoding='utf-8') as f:
    f.write(full_html)

print("Recreated public_staging/aprovacao-credito/index.html successfully from pristine source!")
