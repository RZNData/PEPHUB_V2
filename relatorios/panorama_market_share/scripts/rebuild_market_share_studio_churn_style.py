#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reconstrói o Market Share Studio em public_staging/pep-tools/market-share/index.html
aplicando 100% da arquitetura e identidade visual do Churn Safra (Padrão Ouro):
- Cabeçalho corporativo com gradiente e barra escura .hd-sub
- Painéis .panel com h2 em maiúsculas, .note e .hlp
- Tipografia oficial Segoe UI / Roboto
- Eliminação de bordas arredondadas de 20px (adotando raio sutil de 3px)
- Abas .tabs com classe .on
- Cores 100% alinhadas à paleta corporativa
- Zero emojis
"""

import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def rebuild_studio():
    target = os.path.join("public_staging", "pep-tools", "market-share", "index.html")

    with open(target, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # 1. Substituição do CSS do Studio pelo padrão Churn Safra
    churn_studio_css = """
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
  --accent: #c0392b;
  --radius: 3px;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--ink);
  font: 13px/1.45 "Segoe UI", Roboto, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
}
header { background: #fff; }
.hd-bar {
  background: linear-gradient(90deg, #8a0f18 0%, #c0191f 26%, #e23a1e 50%, #f47a1f 74%, #f9b233 100%);
  display: flex; align-items: center; gap: 16px; padding: 14px 26px;
}
.hd-ico {
  width: 46px; height: 46px; min-width: 46px; border-radius: 50%;
  border: 2.4px solid rgba(255,255,255,.95); display: flex; align-items: center; justify-content: center;
}
.hd-bar h1 {
  margin: 0; color: #fff; font-size: 30px; font-weight: 400; letter-spacing: -.4px; line-height: 1.05;
  display: flex; align-items: baseline; gap: 11px; flex-wrap: wrap;
}
.hd-bar h1 b { font-weight: 800; letter-spacing: -1px; text-transform: none; }
.hd-bar h1 span { font-weight: 300; font-size: 24px; color: rgba(255,255,255,.93); }
.hd-sub {
  background: var(--nav); color: #aab4c0; font-size: 11.5px; padding: 7px 26px;
  display: flex; align-items: center; gap: 10px; flex-wrap: wrap;
}
.hd-sub b { color: #e8edf3; font-weight: 600; }
.hd-sub .dot { width: 3px; height: 3px; border-radius: 50%; background: #5b6675; display: inline-block; }
.hd-sub .hd-right { margin-left: auto; }
.back-hub { color: #f9b233; text-decoration: none; font-weight: 600; display: inline-flex; align-items: center; gap: 4px; transition: color .15s; }
.back-hub:hover { color: #fff; text-decoration: underline; }

.wrap, .workspace { padding: 16px 26px 40px; max-width: 2400px; margin: 0 auto; }
.panel { background: var(--panel); border: 1px solid var(--line); border-radius: 3px; margin-bottom: 14px; }
.panel > h2 {
  margin: 0; padding: 10px 14px; font-size: 12px; font-weight: 600; text-transform: uppercase;
  letter-spacing: .6px; color: var(--ink2); border-bottom: 1px solid var(--line2);
  display: flex; align-items: center; gap: 10px; flex-wrap: wrap;
}
.panel > h2 .note { text-transform: none; letter-spacing: 0; font-weight: 400; color: var(--ink3); font-size: 11px; }
.pbody { padding: 14px; }

/* Botão Help Modal */
.hlp {
  margin-left: auto; width: 19px; height: 19px; min-width: 19px; border-radius: 50%;
  border: 1px solid var(--line); background: #fff; color: var(--ink3);
  font: 600 11px "Segoe UI", Arial; line-height: 1; cursor: pointer;
  display: inline-flex; align-items: center; justify-content: center; padding: 0; flex: none;
}
.hlp:hover { background: var(--nav); color: #fff; border-color: var(--nav); }

/* Tabs Churn Safra */
.tabs { display: flex; gap: 4px; margin-left: auto; flex-wrap: wrap; padding: 8px 14px; background: #fff; border-bottom: 1px solid var(--line2); }
.tab, .tabs button {
  border: 1px solid var(--line); background: #fff; color: var(--ink);
  font-size: 11.5px; padding: 5px 12px; border-radius: 2px; text-decoration: none;
  font-weight: 500; cursor: pointer; transition: background .15s;
}
.tab:hover, .tabs button:hover { background: #f0f2f5; }
.tab.active, .tab.on, .tabs button.on, .tabs button.active {
  background: var(--nav) !important; color: #fff !important; border-color: var(--nav) !important; font-weight: 600;
}

/* KPIs Churn Safra */
.kpis { display: grid; grid-template-columns: repeat(auto-fit, minmax(148px, 1fr)); border: 1px solid var(--line2); background: #fff; border-radius: 3px; margin-bottom: 14px; }
.kpi { padding: 12px 14px; border-right: 1px solid var(--line2); background: #fff; }
.kpi:last-child { border-right: none; }
.kpi .k { font-size: 10.5px; text-transform: uppercase; letter-spacing: .5px; color: var(--ink3); font-weight: 600; }
.kpi .v { font-size: 22px !important; font-weight: 600; margin-top: 3px; letter-spacing: -.3px; color: var(--ink); display: block; line-height: 1.1; }
.kpi .d { font-size: 11px; color: var(--ink2); margin-top: 2px; font-style: normal; display: block; }

/* Controles e Cards */
.card, .preview-card { background: var(--panel); border: 1px solid var(--line); border-radius: 3px; padding: 16px; margin-bottom: 14px; box-shadow: none !important; }
.preview-stage { background: #eef1f3 !important; border: 1px solid var(--line2); border-radius: 3px; padding: 24px; min-height: 420px; }
.btn { border: 1px solid var(--line); background: #fff; color: var(--ink); padding: 5px 12px; border-radius: 2px; font: 12px "Segoe UI", Arial; cursor: pointer; }
.btn:hover { background: #f0f2f5; }
.btn-dark, .btn.primary { background: var(--nav); color: #fff; border-color: var(--nav); }
.btn-dark:hover, .btn.primary:hover { background: var(--nav2); }
.btn-accent, .btn-red { background: var(--red); color: #fff; border-color: var(--red); }
.btn-accent:hover, .btn-red:hover { background: #8a0f18; }
.inp { border: 1px solid var(--line); border-radius: 2px; padding: 6px 10px; font: 12px "Segoe UI", Arial; background: #fff; }
.inp:focus { border-color: var(--blue); outline: none; }
.chart-title-inp { border-bottom: 1px solid var(--line); font-size: 14px; font-weight: 700; color: var(--ink); padding-bottom: 6px; }

/* Ocultar barra antiga com gradientes exóticos */
.appbar { display: none !important; }
.drawer-btn {
  display: inline-flex; align-items: center; gap: 7px; background: var(--nav); color: #fff; border: 1px solid var(--nav);
  border-radius: 2px; font-size: 11.5px; font-weight: 600; text-transform: uppercase; letter-spacing: .5px; padding: 5px 12px; cursor: pointer;
}
"""

    # Substituir bloco <style>...</style>
    content = re.sub(r'<style>.*?</style>', f'<style>\n{churn_studio_css}\n</style>', content, count=1, flags=re.DOTALL)

    # 2. Header Oficial Churn Safra
    official_header = """
<body>

<!-- Header Corporativo Oficial Claro PEP HUB -->
<header>
  <div class="hd-bar">
    <div class="hd-ico">
      <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
        <rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/>
      </svg>
    </div>
    <h1>
      <b>Market Share Studio</b>
      <span>Estúdio de Infográficos & Gráficos Telecom · Regional Norte</span>
    </h1>
    <div style="margin-left:auto; display:flex; align-items:center; gap:8px;">
      <button class="hlp" data-h="scatter" style="display:none">?</button>
      <button class="hlp" data-h="risco" style="display:none">?</button>
      <button class="hlp" data-h="studio" title="Ajuda">?</button>
      <a href="/" class="back-hub">‹ Portal Pephub</a>
    </div>
  </div>
  <div class="hd-sub">
    <span><b>Market Share Studio</b></span>
    <span class="dot"></span>
    <a href="/#pep-tools" style="color:#e8edf3;text-decoration:none;">PeP Tools</a>
    <span class="dot"></span>
    <span>Exportação: <b>SVG Nativo & Imagens de Alta Resolução</b></span>
    <span class="dot"></span>
    <span>Identidade Visual: <b>Padrão Claro Regional Norte</b></span>
    <div class="hd-right">
      <span>Planejamento & Performance</span>
    </div>
  </div>
</header>

<div class="wrap">
"""

    # Inserir após <body>
    content = re.sub(r'<body>.*?(?=<div class="tabs"|<div class="workspace")', official_header, content, count=1, flags=re.DOTALL)
    
    # Fechar .wrap antes de </body>
    content = content.replace('</body>', '</div> <!-- fim .wrap -->\n</body>')

    # 3. Remover todos os emojis informais
    informal_emoji_re = re.compile(
        r'[\U0001F600-\U0001F64F]|[\U0001F300-\U0001F5FF]|[\U0001F680-\U0001F6FF]|[\U0001F900-\U0001F9FF]|[\U0001FA70-\U0001FAFF]'
    )
    content = informal_emoji_re.sub('', content)

    # 4. Adicionar classes .on junto a .active nas tabs
    content = content.replace('class="tab active"', 'class="tab active on"')

    # 5. Adicionar HELP dictionary no script
    help_script = """
<script>
const HELP = {
  studio: "Gerador vetorial de gráficos de Market Share (Pizza, Rosca, Barras, Histórico) 100% alinhados à identidade Claro.",
  scatter: "Visualização de dispersão de share e volume entre concorrentes.",
  risco: "Análise de distribuição e concentração de base."
};
document.addEventListener('click', function(e) {
  if (e.target && e.target.classList && e.target.classList.contains('hlp')) {
    const key = e.target.getAttribute('data-h');
    if (HELP[key]) alert(HELP[key]);
  }
});
</script>
"""
    content = content.replace('</body>', help_script + '\n</body>')

    with open(target, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Market Share Studio reconstruído com sucesso no padrão Churn Safra em {target}")

if __name__ == "__main__":
    rebuild_studio()
