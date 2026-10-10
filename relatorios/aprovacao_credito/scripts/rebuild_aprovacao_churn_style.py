#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reconstrói a Taxa de Aprovação de Crédito PF (RNO Cidade e PDV)
em public_staging/aprovacao-credito/index.html
aplicando 100% da arquitetura e identidade visual do Churn Safra (Padrão Ouro):
- Cabeçalho oficial com gradiente horizontal Claro e barra escura .hd-sub
- Substituição da barra lateral escura por Painel de Abas .tabs no topo
- Painéis .panel padronizados com h2 em maiúsculas, .note e .hlp
- KPIs em grade oficial Churn Safra (.kpi .k / .v 22px / .d)
- Remoção do hero escuro não-padrão (.chero)
- Paleta semântica estrita do Churn Safra
- Biblioteca local xlsx.full.min.js (Zero CDNs)
- Zero emojis
"""

import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def rebuild_aprovacao():
    src_file = "Painel Aprovacao Credito RNO 2.4.html"
    dst_file = os.path.join("public_staging", "aprovacao-credito", "index.html")

    with open(src_file, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # 1. Substituir CDN pelo script local
    content = content.replace(
        '<script src="https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js"></script>',
        '<script src="xlsx.full.min.js"></script>'
    )

    # 2. Extrair estilos, corpo e scripts
    # Estilo Churn Safra completo para Aprovação de Crédito
    churn_css = """
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

.wrap { padding: 16px 26px 40px; max-width: 2400px; margin: 0 auto; }
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
.tabs { display: flex; gap: 4px; margin-left: auto; flex-wrap: wrap; }
.tabs a, .tabs button {
  border: 1px solid var(--line); background: #fff; color: var(--ink);
  font-size: 11.5px; padding: 5px 12px; border-radius: 2px; text-decoration: none;
  font-weight: 500; cursor: pointer; transition: background .15s;
}
.tabs a:hover, .tabs button:hover { background: #f0f2f5; }
.tabs a.on, .tabs a.active, .tabs button.on, .tabs button.active {
  background: var(--nav) !important; color: #fff !important; border-color: var(--nav) !important; font-weight: 600;
}

/* KPIs Churn Safra */
.kpis { display: grid; grid-template-columns: repeat(auto-fit, minmax(148px, 1fr)); border: 1px solid var(--line2); background: #fff; border-radius: 3px; margin-bottom: 14px; }
.kpi { padding: 12px 14px; border-right: 1px solid var(--line2); background: #fff; }
.kpi:last-child { border-right: none; }
.kpi .k, .kpi .lab { font-size: 10.5px; text-transform: uppercase; letter-spacing: .5px; color: var(--ink3); font-weight: 600; }
.kpi .v, .kpi .val, .lvlcount .lc-num { font-size: 22px !important; font-weight: 600; margin-top: 3px; letter-spacing: -.3px; color: var(--ink); display: block; line-height: 1.1; }
.kpi .d, .kpi .sub, .kpi .dl { font-size: 11px; color: var(--ink2); margin-top: 2px; font-style: normal; display: block; }
.up { color: var(--green) !important; }
.down { color: var(--red) !important; }
.mut { color: var(--ink3) !important; }

/* Filtros Globais */
.filters {
  background: #fff; border: 1px solid var(--line); border-radius: 3px;
  padding: 10px 14px; margin-bottom: 14px; display: flex; flex-wrap: wrap; gap: 12px; align-items: flex-start;
}
.fgroup { display: flex; flex-direction: column; gap: 4px; }
.fgroup label { font-size: 10.5px; text-transform: uppercase; letter-spacing: .5px; color: var(--ink3); font-weight: 700; }
.msdd { position: relative; border: 1px solid var(--line); border-radius: 2px; background: #fff; min-width: 170px; }
.msdd > summary { padding: 5px 10px; font-size: 12px; font-weight: 600; color: var(--ink); cursor: pointer; display: flex; justify-content: space-between; align-items: center; }
.msbody { position: absolute; top: calc(100% + 2px); left: 0; z-index: 50; background: #fff; border: 1px solid var(--line); border-radius: 3px; box-shadow: 0 8px 24px rgba(0,0,0,.15); padding: 8px; min-width: 240px; max-height: 320px; overflow: auto; }
.msitem { display: flex; align-items: center; gap: 6px; padding: 4px; font-size: 12px; cursor: pointer; border-radius: 2px; }
.msitem:hover { background: #f0f2f5; }
.msitem input { accent-color: var(--red); }
.drawer-btn {
  display: inline-flex; align-items: center; gap: 7px; background: var(--nav); color: #fff; border: 1px solid var(--nav);
  border-radius: 2px; font-size: 11.5px; font-weight: 600; text-transform: uppercase; letter-spacing: .5px; padding: 5px 12px; cursor: pointer;
}
.drawer-btn:hover { background: var(--nav2); }

/* Tabelas Analíticas */
.tablewrap, .dualscroll .ds-body { overflow-x: auto; border: 1px solid var(--line2); border-radius: 3px; background: #fff; }
table { width: 100%; border-collapse: collapse; font-size: 12px; }
th, td { padding: 6px 8px; border-bottom: 1px solid var(--line2); text-align: right; white-space: nowrap; }
th { background: #f7f8fa; color: var(--ink2); font-weight: 600; font-size: 10.5px; text-transform: uppercase; letter-spacing: .3px; position: sticky; top: 0; z-index: 2; border-bottom: 1px solid var(--line); }
th:first-child, td:first-child { text-align: left; }
tbody tr:hover { background: #f7f9fb; }
.card { background: var(--panel); border: 1px solid var(--line); border-radius: 3px; padding: 14px; margin-bottom: 14px; }
.card h3 { font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: .5px; color: var(--ink2); margin-bottom: 4px; }
.card .csub { font-size: 11px; color: var(--ink3); margin-bottom: 12px; }

/* Limpeza de cores escuras ou exóticas para o padrão sóbrio Churn Safra */
.cbadge.ci { background: #eaf2ec; color: var(--green); }
.cbadge.cs { background: #eef2f6; color: var(--blue); }
.cbadge.ce { background: #fdf3e2; color: var(--amber); }

/* Removendo heróis pretos e substituindo por cards brancos */
.chero { background: #fff !important; color: var(--ink) !important; border: 1px solid var(--line); border-radius: 3px; box-shadow: none !important; margin-bottom: 14px; padding: 14px; }
.chero h2 { color: var(--ink) !important; font-size: 20px; font-weight: 700; margin-bottom: 8px; }
.chero .lead { color: var(--ink2) !important; font-size: 12.5px; }
.chero .fignum { color: var(--ink) !important; font-size: 32px !important; }
.chero .figlab { color: var(--ink3) !important; }
.cta-bar { background: #f7f8fa !important; color: var(--ink) !important; border: 1px solid var(--line); border-radius: 3px; padding: 12px 16px; margin-bottom: 14px; box-shadow: none !important; }
.cta-bar .txt h4 { color: var(--ink) !important; font-size: 13px; font-weight: 700; }
.cta-bar .txt p { color: var(--ink2) !important; font-size: 11.5px; }
.cta-bar .goact { background: var(--nav) !important; color: #fff !important; border-radius: 2px; padding: 6px 14px; font-size: 11.5px; }
.hlcard { background: #fff !important; border: 1px solid var(--line); border-radius: 3px; padding: 12px 14px; box-shadow: none !important; }
.hlcard .k { font-size: 10px; font-weight: 700; text-transform: uppercase; color: var(--ink3); }
.hlcard .v { font-size: 18px; font-weight: 700; color: var(--ink); }

/* Ocultar barra lateral antiga e garantir layout full width Churn Safra */
#app { display: block !important; }
#side { display: none !important; }
#main { margin-left: 0 !important; width: 100% !important; }
.topbar { display: none !important; } /* substituída pelo header oficial */
"""

    # 3. Remover a tag <style>...</style> antiga e inserir churn_css
    content = re.sub(r'<style>.*?</style>', f'<style>\n{churn_css}\n</style>', content, count=1, flags=re.DOTALL)

    # 4. Inserir Header Corporativo Oficial Claro PEP HUB e Navegação por Tabs logo após <body>
    header_markup = """
<body>

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
    <a href="/" class="back-hub" style="margin-left:auto;">‹ Portal Pephub</a>
  </div>
  <div class="hd-sub">
    <span><b>Aprovação de Crédito PF</b></span>
    <span class="dot"></span>
    <span>Posição Oficial: <b>Ago/2026</b></span>
    <span class="dot"></span>
    <span>Regional Norte (AM · AP · MA · PA · PI · RR)</span>
    <span class="dot"></span>
    <span>Escopo: <b>Cidades e Redes de PDVs</b></span>
    <div class="hd-right">
      <span>Planejamento & Performance</span>
    </div>
  </div>
</header>

<div class="wrap">

  <!-- Painel de Navegação Executiva (Tabs Churn Safra que controlam o roteamento dinâmico original) -->
  <div class="panel" style="margin-bottom:14px;">
    <h2>VISÕES DO PAINEL <span class="note">Aberturas analíticas de aprovação, canais, PDVs e risco de inadimplência</span> <button class="hlp" data-h="risco">?</button></h2>
    <div class="pbody" style="padding:8px 14px;">
      <nav class="tabs" id="nav" style="margin-left:0;">
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
    </div>
  </div>
"""

    # Inserir no início do <body> substituindo o início de #app e aside
    content = re.sub(r'<body>\s*<div id="app">', header_markup + '\n<div id="app">', content, count=1)

    # 5. Adicionar fechamento de .wrap antes de </body>
    content = content.replace('</body>', '</div> <!-- fim .wrap -->\n</body>')

    # 6. Remover todos os emojis informais
    informal_emoji_re = re.compile(
        r'[\U0001F600-\U0001F64F]|[\U0001F300-\U0001F5FF]|[\U0001F680-\U0001F6FF]|[\U0001F900-\U0001F9FF]|[\U0001FA70-\U0001FAFF]'
    )
    content = informal_emoji_re.sub('', content)

    # 7. Adicionar HELP dictionary e botão drawer para conformidade
    help_code = """
<script>
const HELP = {
  risco: "Direcionamento analítico de concessão de crédito residencial PF: limiares de aprovação, curvas de inadimplência e identificação de fraudes na Regional Norte.",
  filtros: "Filtros multidimensionais por Estado, DDD, Praça, Canal de Venda e Rede de PDVs.",
  visoes: "Selecione entre Capa Executiva, Visão Geral, Canais & PDVs, Visão Diária, Carteira e Insights."
};
document.addEventListener('click', function(e) {
  if (e.target && e.target.classList && e.target.classList.contains('hlp')) {
    const key = e.target.getAttribute('data-h');
    if (HELP[key]) alert(HELP[key]);
  }
});
</script>
"""
    content = content.replace('</body>', help_code + '\n</body>')

    with open(dst_file, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Painel de Aprovação de Crédito reconstruído com sucesso no padrão Churn Safra em {dst_file}")

if __name__ == "__main__":
    rebuild_aprovacao()
