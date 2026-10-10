#!/usr/bin/env python3
"""
Integra o Market Share Studio (market_share_studio_v3_50.html) na seção PeP Tools do public_staging/,
tornando-o 100% autocontido, offline e aderente aos padrões de design corporativo da Claro / PEP HUB.
"""

import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def integrate_market_share():
    src_file = "market_share_studio_v3_50.html"
    dest_file = os.path.join("public_staging", "pep-tools", "market-share", "index.html")

    print(f"Lendo {src_file}...")
    with open(src_file, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Substituir CDN do XLSX pelo script local
    html = re.sub(
        r'<script src="https://cdn\.jsdelivr\.net/npm/xlsx[^"]+"[^>]*></script>',
        '<script src="xlsx.full.min.js" onerror="window.__xlsxFail=1"></script>',
        html
    )

    # 2. Desacoplar Google Fonts externa mantendo font-stack rica e local
    html = re.sub(
        r'<link href="https://fonts\.googleapis\.com/css2\?family=Montserrat[^"]+" rel="stylesheet">',
        '<!-- Fontes locais e nativas de alta resolução -->',
        html
    )

    # 3. CSS de Cabeçalho Corporativo e Staging Banner
    pep_header_css = """
/* PEP HUB Brand & Staging Integration */
.staging-banner {
  background: linear-gradient(90deg, #6366f1, #8b5cf6, #ec4899);
  color: #fff;
  padding: 7px 24px;
  font-size: 11px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(255,255,255,0.25);
  position: relative;
  z-index: 100;
}
.staging-pill {
  background: rgba(0,0,0,0.3);
  padding: 2px 10px;
  border-radius: 999px;
  font-size: 10px;
  text-transform: uppercase;
}
.pep-top-bar {
  background: linear-gradient(90deg, #8a0f18 0%, #c0191f 26%, #e23a1e 50%, #f47a1f 74%, #f9b233 100%);
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 10px 24px;
  color: #fff;
  border-bottom: 1px solid rgba(0,0,0,0.1);
  position: relative;
  z-index: 95;
}
.pep-top-ico {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  border: 2px solid rgba(255,255,255,0.95);
  display: flex;
  align-items: center;
  justify-content: center;
}
.pep-top-bar h1 {
  margin: 0;
  color: #fff;
  font-size: 18px;
  font-weight: 400;
  line-height: 1.1;
  display: flex;
  align-items: baseline;
  gap: 8px;
}
.pep-top-bar h1 b { font-weight: 800; }
.pep-top-bar h1 span { font-weight: 300; font-size: 15px; color: rgba(255,255,255,0.92); }
.pep-top-actions {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 8px;
}
.pep-btn-link {
  background: rgba(255,255,255,0.2);
  color: #fff;
  border: 1px solid rgba(255,255,255,0.35);
  padding: 5px 12px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  transition: background .15s;
}
.pep-btn-link:hover { background: rgba(255,255,255,0.35); color: #fff; }
"""
    html = html.replace("</style>", pep_header_css + "\n</style>")

    # 4. Inserir Banner e Header no início de <body>
    pep_header_html = """<body>
<!-- Staging Banner -->
<div class="staging-banner">
  <span>🧪 <b>AMBIENTE SECUNDÁRIO DE TESTE (STAGING)</b> — Market Share Studio Telecom & Infográficos</span>
  <span class="staging-pill">Staging Preview</span>
</div>

<!-- Header PEP HUB Corporativo -->
<div class="pep-top-bar">
  <div class="pep-top-ico">
    <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
      <line x1="18" y1="20" x2="18" y2="10"/>
      <line x1="12" y1="20" x2="12" y2="4"/>
      <line x1="6" y1="20" x2="6" y2="14"/>
    </svg>
  </div>
  <h1>
    <b>Market Share Studio</b>
    <span>· Telecom & Infográficos PeP Tools</span>
  </h1>
  <div class="pep-top-actions">
    <a href="/pep-tools/aniversario/" class="pep-btn-link">Cards de Aniversário TV</a>
    <a href="/pep-tools/divulgacao/" class="pep-btn-link">‹ Divulgação TV</a>
    <a href="/" class="pep-btn-link">‹ Portal Pephub</a>
  </div>
</div>
"""
    html = html.replace("<body>", pep_header_html, 1)

    print(f"Escrevendo {dest_file}...")
    with open(dest_file, "w", encoding="utf-8") as f:
        f.write(html)

    size_kb = os.path.getsize(dest_file) / 1024
    print(f"✅ Market Share Studio integrado com sucesso! ({size_kb:.1f} KB)")

if __name__ == "__main__":
    integrate_market_share()
