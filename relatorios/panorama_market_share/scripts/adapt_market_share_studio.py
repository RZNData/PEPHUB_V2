#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Adequação completa do Market Share Studio (PeP Tools)
em public_staging/pep-tools/market-share/index.html ao PADRAO_DESIGN_PAINEIS.md:
- 13 variáveis de design system em :root
- Cabeçalho institucional Claro com gradiente e barra de contexto .hd-sub
- Tipografia corporativa Segoe UI / Roboto
- Eliminação de todos os emojis informais
- Suporte a .tabs .on para abas ativas
- Indicadores de KPI padronizados (22px)
- Dicionário de ajuda HELP
"""

import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def adapt_studio():
    target = os.path.join("public_staging", "pep-tools", "market-share", "index.html")
    with open(target, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()

    # 1. Variáveis CSS em :root
    old_root_re = r':root\s*\{[^}]+\}'
    new_root = """:root {
  --bg: #f4f6f9;
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
  --radius: 8px;
}"""
    html = re.sub(old_root_re, new_root, html, count=1)

    # 2. Tipografia e estilos adicionais PEP HUB
    extra_css = """
/* PEP HUB Design System Standards */
body { font-family: "Segoe UI", Roboto, Arial, sans-serif !important; }
.hd-bar {
  background: linear-gradient(90deg, #8a0f18 0%, #c0191f 26%, #e23a1e 50%, #f47a1f 74%, #f9b233 100%);
  padding: 12px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: #fff;
}
.hd-bar h1 { font-size: 18px; font-weight: 800; margin: 0; color: #fff; }
.hd-bar h1 span { font-weight: 300; font-size: 13.5px; opacity: 0.92; color: #fff; }
.hd-sub {
  background: var(--nav);
  padding: 8px 24px;
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 11.5px;
  color: #c9d2df;
  border-bottom: 1px solid rgba(255,255,255,0.08);
  flex-wrap: wrap;
}
.hd-sub a { color: #fff; text-decoration: none; font-weight: 600; }
.hd-sub a:hover { text-decoration: underline; }
.hd-sub .dot { width: 4px; height: 4px; border-radius: 50%; background: rgba(255,255,255,0.4); display: inline-block; }
.drawer-btn {
  background: rgba(255,255,255,0.15);
  border: 1px solid rgba(255,255,255,0.3);
  color: #fff;
  padding: 5px 12px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
}
.hlp {
  width: 19px; height: 19px; min-width: 19px; border-radius: 50%;
  border: 1px solid var(--line); background: #fff; color: var(--ink3);
  font: 600 11px "Segoe UI", Arial; cursor: pointer; display: inline-flex;
  align-items: center; justify-content: center;
}
.hlp:hover { background: var(--nav); color: #fff; border-color: var(--nav); }
.kpis { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 10px; margin-bottom: 12px; }
.kpi { background: var(--card); border: 1px solid var(--line); border-radius: 4px; padding: 10px 14px; }
.kpi .v { font-size: 22px !important; font-weight: 800; color: var(--ink); }
.kpi .k { font-size: 10.5px; text-transform: uppercase; color: var(--ink3); font-weight: 600; letter-spacing: 0.5px; }
.kpi .d { font-size: 10px; color: var(--ink2); margin-top: 2px; }
.tab.on, .tab.active { background: var(--nav) !important; color: #fff !important; }
"""
    html = html.replace("</style>", extra_css + "\n</style>")

    # 3. Remover emojis informais do arquivo
    informal_emoji_re = re.compile(
        r'[\U0001F600-\U0001F64F]|[\U0001F300-\U0001F5FF]|[\U0001F680-\U0001F6FF]|[\U0001F900-\U0001F9FF]|[\U0001FA70-\U0001FAFF]'
    )
    # Substituir emojis por string vazia ou símbolos técnicos
    html = informal_emoji_re.sub('', html)

    # 4. Inserir Header Corporativo Oficial Claro PEP HUB logo após <body>
    header_html = """
<!-- Staging Banner -->
<div style="background:#0f172a; color:#f8fafc; font-size:11px; padding:6px 24px; display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid rgba(255,255,255,0.1);">
  <span>[STAGING] <b>AMBIENTE SECUNDÁRIO DE TESTE</b> — Market Share Studio 3.0 (PeP Tools)</span>
  <span style="background:rgba(234,179,8,0.2); color:#fef08a; padding:2px 8px; border-radius:999px; font-weight:700;">Staging Preview</span>
</div>

<!-- Header Corporativo Oficial Claro PEP HUB -->
<header>
  <div class="hd-bar">
    <div style="display:flex; align-items:center; gap:12px;">
      <div style="width:34px; height:34px; border-radius:50%; border:2.4px solid rgba(255,255,255,.95); display:flex; align-items:center; justify-content:center; background:rgba(255,255,255,0.15);">
        <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"/><path d="M12 2a10 10 0 0 1 10 10"/><path d="M12 12 2.5 7.5"/>
        </svg>
      </div>
      <h1>
        <b>Market Share Studio 3.0</b>
        <span>· Gerador de Gráficos Telecom · Regional Norte</span>
      </h1>
    </div>
    <div style="display:flex; align-items:center; gap:10px;">
      <button class="drawer-btn" onclick="document.querySelector('.appbar')?.classList.toggle('collapsed')">Opções</button>
      <button class="hlp" data-h="studio" title="Ajuda sobre o Gerador de Gráficos">?</button>
      <button class="hlp" data-h="scatter" title="Ajuda sobre Dispersão" style="display:none">?</button>
      <button class="hlp" data-h="risco" title="Ajuda sobre Risco" style="display:none">?</button>
      <a href="/" class="drawer-btn" style="text-decoration:none;">‹ Portal Pephub</a>
    </div>
  </div>
  <div class="hd-sub">
    <a href="/">‹ Portal Pephub</a>
    <span class="dot"></span>
    <a href="/#pep-tools">‹ PeP Tools</a>
    <span class="dot"></span>
    <span>Módulo: <b>Estúdio de Gráficos & Infográficos de Market Share</b></span>
    <span class="dot"></span>
    <span>Exportação: <b>SVG Nativo & PNG Alta Resolução</b></span>
    <div style="margin-left:auto; font-size:11px; opacity:0.8;">Regional Norte · Planejamento & Performance</div>
  </div>
</header>
"""
    # Substituir <header class="appbar"> existente ou inserir após <body>
    html = re.sub(r'<body[^>]*>', r'<body>\n' + header_html, html, count=1, flags=re.I)

    # 5. Adicionar classe 'on' junto de 'active' nas tabs
    html = html.replace('class="tab active"', 'class="tab active on"')

    # 6. Inserir dicionário HELP no final antes de </body>
    help_script = """
<script>
const HELP = {
  studio: "Ferramenta para geração de gráficos vetoriais (Pizza, Rosca, Barras, Histórico e Tabela) de Market Share nos padrões visuais Claro.",
  scatter: "Visualização de dispersão de share e volume entre concorrentes.",
  risco: "Análise de distribuição e exposição mercadológica."
};
document.addEventListener('click', function(e) {
  if (e.target && e.target.classList && e.target.classList.contains('hlp')) {
    const key = e.target.getAttribute('data-h');
    if (HELP[key]) alert(HELP[key]);
  }
});
</script>
"""
    html = html.replace("</body>", help_script + "\n</body>")

    with open(target, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ Market Share Studio adaptado em {target}")

if __name__ == "__main__":
    adapt_studio()
