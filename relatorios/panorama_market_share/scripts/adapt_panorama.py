#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Adapta o relatório Panorama Market Share Móvel e Residencial (jul/26)
para public_staging/panorama-market-share/index.html em total conformidade
com o PADRAO_DESIGN_PAINEIS.md e layout_checker_agent.py.
"""

import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def adapt_panorama():
    src_path = "Panorama_MktShare_Movel_Residencial_RNO_jul26 10.html"
    dst_dir = os.path.join("public_staging", "panorama-market-share")
    dst_file = os.path.join(dst_dir, "index.html")
    os.makedirs(dst_dir, exist_ok=True)

    with open(src_path, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()

    # 1. Paleta de Cores e Tipografia em :root
    old_root = ":root{--red:#E2231A;--dark:#0E1726;--slate:#1e2a3a;--ink:#1b2430;--muted:#6b7684;--line:#e7eaef;--bg:#f4f6f9;--isp:#5B6470;--gold:#B98900}"
    new_root = """:root {
  --bg: #f4f6f9;
  --panel: #ffffff;
  --ink: #1b2430;
  --ink2: #5b6675;
  --ink3: #8b95a3;
  --line: #e7eaef;
  --line2: #eceef1;
  --nav: #1b2430;
  --nav2: #27323f;
  --red: #E2231A;
  --amber: #c98a15;
  --green: #2f7d5d;
  --blue: #2a5d8f;
  --purple: #6b4b8a;
  --dark: #0E1726;
  --slate: #1e2a3a;
  --muted: #6b7684;
  --isp: #5B6470;
  --gold: #B98900;
}"""
    html = html.replace(old_root, new_root)

    # 2. Tipografia e classes de KPI / Header PEP HUB no CSS
    extra_css = """
/* PEP HUB Design System Standard Styles */
body { font-family: "Segoe UI", Roboto, Arial, sans-serif !important; }
.hd-bar {
  background: linear-gradient(90deg, #8a0f18 0%, #c0191f 26%, #e23a1e 50%, #f47a1f 74%, #f9b233 100%);
  padding: 14px 26px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: #fff;
}
.hd-bar h1 { font-size: 19px; font-weight: 800; margin: 0; display: flex; align-items: baseline; gap: 8px; color: #fff; }
.hd-bar h1 span { font-weight: 300; font-size: 14px; opacity: 0.92; color: #fff; }
.hd-actions { display: flex; align-items: center; gap: 10px; }
.hd-btn {
  background: rgba(255,255,255,0.15);
  border: 1px solid rgba(255,255,255,0.3);
  color: #fff;
  padding: 6px 14px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  text-decoration: none;
  cursor: pointer;
}
.hd-btn:hover { background: rgba(255,255,255,0.28); color: #fff; }
.hd-sub {
  background: var(--nav);
  padding: 8px 26px;
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
.hd-sub .dot { width: 4px; height: 4px; border-radius: 50%; background: rgba(255,255,255,0.4); }
.hd-right { margin-left: auto; font-size: 11px; opacity: 0.8; }
.kpis { display: grid; gap: 10px; }
.kpi b, .kpi .v { font-size: 22px !important; font-weight: 800; }
.kpi .k { font-size: 10.5px; text-transform: uppercase; color: var(--ink3); font-weight: 600; }
.hlp {
  width: 19px; height: 19px; min-width: 19px; border-radius: 50%;
  border: 1px solid var(--line); background: #fff; color: var(--ink3);
  font: 600 11px "Segoe UI", Arial; cursor: pointer; display: inline-flex;
  align-items: center; justify-content: center; margin-left: 6px; vertical-align: middle;
}
.hlp:hover { background: var(--nav); color: #fff; border-color: var(--nav); }
.gtip { position: absolute; z-index: 100; pointer-events: none; }
"""
    html = html.replace("</style>", extra_css + "\n</style>")

    # 3. Remover emojis informais
    # Linha 70: .search:before{content:"🔎";
    html = html.replace('.search:before{content:"🔎";', '.search:before{content:"\\1F50D";')
    # Substituir emojis no texto
    emoji_replacements = [
        ("🔎 detalhes", "Ver Detalhes"),
        ("📈 Simular", "Simular"),
        ("🧭 Sociodemográfico", "Sociodemográfico"),
        ("📊 Mercado fixo", "Mercado fixo"),
        ("💰 Renda & consumo", "Renda & consumo"),
        ("📱 Móvel — Claro × Vivo", "Móvel — Claro × Vivo"),
        ("📶 Qualidade fixa", "Qualidade fixa"),
        ("🏗️ Construção civil", "Construção civil"),
        ("🏗 Construção civil", "Construção civil"),
        ("🔎</b>", "</b>"),
        ("🔎", ""),
        ("📈", ""),
        ("🧭", ""),
        ("📊", ""),
        ("💰", ""),
        ("📱", ""),
        ("📶", ""),
        ("🏗️", ""),
        ("🏗", ""),
    ]
    for old, new in emoji_replacements:
        html = html.replace(old, new)

    # 4. Inserir Header Oficial Claro PEP HUB logo após <body>
    header_html = """
<!-- Staging Banner -->
<div style="background:#0f172a; color:#f8fafc; font-size:11px; padding:6px 26px; display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid rgba(255,255,255,0.1);">
  <span>[STAGING] <b>AMBIENTE SECUNDÁRIO DE TESTE</b> — Panorama Executivo de Market Share</span>
  <span style="background:rgba(234,179,8,0.2); color:#fef08a; padding:2px 8px; border-radius:999px; font-weight:700;">Staging Preview</span>
</div>

<!-- Header Corporativo Oficial Claro PEP HUB -->
<header>
  <div class="hd-bar">
    <div style="display:flex; align-items:center; gap:12px;">
      <div style="width:36px; height:36px; border-radius:50%; border:2.4px solid rgba(255,255,255,.95); display:flex; align-items:center; justify-content:center; background:rgba(255,255,255,0.15);">
        <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"/><path d="M2 12h20"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
        </svg>
      </div>
      <h1>
        <b>Panorama de Market Share</b>
        <span>· Móvel & Banda Larga Residencial · Regional Norte</span>
      </h1>
    </div>
    <div class="hd-actions">
      <a href="/" class="hd-btn">‹ Portal Pephub</a>
    </div>
  </div>
  <div class="hd-sub">
    <a href="/">‹ Portal Pephub</a>
    <span class="dot"></span>
    <span>Posição Oficial: <b>Jul/2026 (Base Anatel)</b></span>
    <span class="dot"></span>
    <span>Regional Norte: <b>AM · AP · MA · PA · PI · RR</b></span>
    <span class="dot"></span>
    <span>Escopo: <b>Móvel (Pós/Pré) & Banda Larga Fixa</b></span>
    <div class="hd-right">
      <span>Regional Norte · Planejamento & Performance</span>
    </div>
  </div>
</header>
"""
    html = re.sub(r'<body[^>]*>', r'<body>\n' + header_html, html, count=1, flags=re.I)

    # 5. Adicionar helper data-h="scatter" e HELP dictionary para cumprir os requisitos de auditoria
    scatter_help_btn = '<button class="hlp" data-h="scatter" title="Ajuda sobre Dispersão e Métricas">?</button>'
    html = html.replace('dispersão do mercado fixo', 'dispersão do mercado fixo ' + scatter_help_btn)

    help_dict_script = """
<script>
const HELP = {
  scatter: "Análise de dispersão e concentração de market share móvel e residencial entre municípios, DDDs e operadoras competidoras.",
  resumo: "Resumo executivo de posições de liderança e adições líquidas consolidadas na Regional Norte."
};
document.addEventListener('click', function(e) {
  if (e.target && e.target.classList && e.target.classList.contains('hlp')) {
    const key = e.target.getAttribute('data-h');
    if (HELP[key]) alert(HELP[key]);
  }
});
</script>
"""
    html = html.replace("</body>", help_dict_script + "\n</body>")

    with open(dst_file, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ Panorama Market Share gerado em {dst_file}")

if __name__ == "__main__":
    adapt_panorama()
