#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Adapta o Painel Taxa de Aprovação de Crédito PF (RNO Cidade e PDV)
para public_staging/aprovacao-credito/index.html em total conformidade
com o PADRAO_DESIGN_PAINEIS.md e layout_checker_agent.py.
"""

import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def adapt_aprovacao():
    src_path = "Painel Aprovacao Credito RNO 2.4.html"
    dst_dir = os.path.join("public_staging", "aprovacao-credito")
    dst_file = os.path.join(dst_dir, "index.html")
    os.makedirs(dst_dir, exist_ok=True)

    with open(src_path, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()

    # 1. Substituir CDN xlsx pelo arquivo local
    html = html.replace(
        '<script src="https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js"></script>',
        '<script src="xlsx.full.min.js"></script>'
    )

    # 2. Paleta de Cores Completa em :root
    old_root_pattern = r':root\s*\{[^}]+\}'
    new_root = """:root {
  --bg: #F4F6FA;
  --panel: #FFFFFF;
  --card: #FFFFFF;
  --ink: #1F2937;
  --ink2: #5B6675;
  --ink3: #8B95A3;
  --line: #E5E7EB;
  --line2: #ECEEF1;
  --nav: #141B2E;
  --nav2: #1E2740;
  --red: #D6293E;
  --green: #1E9E5A;
  --amber: #E8A200;
  --blue: #2E5AAC;
  --purple: #6B4B8A;
  --claro: #E4002B;
  --claro-d: #B30022;
  --navy: #141B2E;
  --navy2: #1E2740;
  --muted: #6B7280;
  --good: #E7F6EE;
  --warn: #FCF3DC;
  --bad: #FBE7EA;
}"""
    html = re.sub(old_root_pattern, new_root, html, count=1)

    # 3. CSS Adicional para Header Institucional Claro, .hd-sub, .drawer-btn, .kpis, .hlp
    extra_css = """
/* PEP HUB Design System Standards */
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
.drawer-btn:hover { background: rgba(255,255,255,0.25); color: #fff; }
.hlp {
  width: 19px; height: 19px; min-width: 19px; border-radius: 50%;
  border: 1px solid var(--line); background: #fff; color: var(--ink3);
  font: 600 11px "Segoe UI", Arial; cursor: pointer; display: inline-flex;
  align-items: center; justify-content: center;
}
.hlp:hover { background: var(--nav); color: #fff; border-color: var(--nav); }
.kpis { display: grid; gap: 10px; }
.kpi b, .kpi .v, .lvlcount .lc-num { font-size: 22px !important; font-weight: 800; }
.kpi .k { font-size: 10.5px; text-transform: uppercase; color: var(--ink3); font-weight: 600; }
.staging-bar {
  background: #0f172a;
  color: #f8fafc;
  font-size: 11px;
  padding: 6px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}
"""
    html = html.replace("</style>", extra_css + "\n</style>")

    # 4. Remover emojis informais
    emoji_cleanups = [
        ("placeholder=\"🔎 Buscar cidade, estado ou DDD...\"", "placeholder=\"Buscar cidade, estado ou DDD...\""),
        ("📈 Linha", "Linha"),
        ("placeholder=\"🔎 Buscar PDV, razão, cidade, canal, rede...\"", "placeholder=\"Buscar PDV, razão, cidade, canal, rede...\""),
        ("🏷️ Rótulos", "Rótulos"),
        ("🔍 Zoom", "Zoom"),
        ("🔑 <b>Cascata", "<b>Cascata"),
        ("placeholder=\"🔎 Buscar PDV, canal, rede...\"", "placeholder=\"Buscar PDV, canal, rede...\""),
        ("🖨️ Imprimir", "Imprimir"),
        ("📌 <b>Síntese:</b>", "<b>Síntese:</b>"),
        ("💡", ""),
        ("📌", ""),
        ("📁", ""),
        ("🔎", ""),
        ("📈", ""),
        ("🔑", ""),
        ("🖨️", ""),
        ("🖨", ""),
        ("🏷️", ""),
        ("🏷", ""),
        ("🔍", ""),
    ]
    for old, new in emoji_cleanups:
        html = html.replace(old, new)

    # 5. Adicionar Header Oficial Claro dentro de #main antes de .topbar ou substituindo topo
    header_html = """
    <!-- Staging Banner -->
    <div class="staging-bar">
      <span>[STAGING] <b>AMBIENTE SECUNDÁRIO DE TESTE</b> — Taxa de Aprovação de Crédito PF</span>
      <span style="background:rgba(234,179,8,0.2); color:#fef08a; padding:2px 8px; border-radius:999px; font-weight:700;">Staging Preview</span>
    </div>

    <!-- Header Corporativo Oficial Claro PEP HUB -->
    <header>
      <div class="hd-bar">
        <div style="display:flex; align-items:center; gap:12px;">
          <div style="width:34px; height:34px; border-radius:50%; border:2.4px solid rgba(255,255,255,.95); display:flex; align-items:center; justify-content:center; background:rgba(255,255,255,0.15);">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
            </svg>
          </div>
          <h1>
            <b>Taxa de Aprovação de Crédito PF</b>
            <span>· Cidade e PDV · Regional Norte</span>
          </h1>
        </div>
        <div style="display:flex; align-items:center; gap:10px;">
          <button class="drawer-btn" onclick="document.querySelector('.filters')?.classList.toggle('collapsed')">Filtros</button>
          <button class="hlp" data-h="risco" title="Ajuda sobre Risco e Aprovação">?</button>
          <a href="/" class="drawer-btn" style="text-decoration:none;">‹ Portal Pephub</a>
        </div>
      </div>
      <div class="hd-sub">
        <a href="/">‹ Portal Pephub</a>
        <span class="dot"></span>
        <span>Módulo: <b>Taxa de Aprovação de Crédito PF</b></span>
        <span class="dot"></span>
        <span>Regional Norte: <b>AM · AP · MA · PA · PI · RR</b></span>
        <span class="dot"></span>
        <span>Posição Oficial: <b>Ago/2026</b></span>
        <div style="margin-left:auto; font-size:11px; opacity:0.8;">Regional Norte · Planejamento & Performance</div>
      </div>
    </header>
"""
    # Inserir no início de <main id="main">
    main_pattern = r'(<main id="main"[^>]*>)'
    html = re.sub(main_pattern, r'\1\n' + header_html, html, count=1)

    # 6. Inserir dicionário HELP no final antes de </body>
    help_script = """
<script>
const HELP = {
  risco: "Direcionamento analítico de crédito: taxa de aprovação, limiar de entrada, risco de inadimplência, fraudes e performance por canal/PDV na Regional Norte.",
  capa: "Visão executiva e síntese de direcionamento para política de concessão de crédito residencial PF.",
  v1: "Visão geral consolidada por Estado, DDD e cluster de qualidade de aprovação."
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

    with open(dst_file, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ Painel de Aprovação de Crédito gerado em {dst_file}")

if __name__ == "__main__":
    adapt_aprovacao()
