#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reconstrói o Panorama Market Share Móvel e Residencial (jul/26)
em public_staging/panorama-market-share/index.html
aplicando 100% da arquitetura e identidade visual do Churn Safra (Padrão Ouro):
- Cabeçalho oficial com gradiente e barra escura .hd-sub
- Painéis .panel com h2 em maiúsculas, .note e .hlp
- Paleta semântica estrita do Churn Safra (sem cores vibrantes fora do padrão)
- Tabelas limpas com th #f7f8fa e td com bordas sutis
- Abas .tabs com .on
- Zero emojis
"""

import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def rebuild_panorama():
    src_file = "Panorama_MktShare_Movel_Residencial_RNO_jul26 10.html"
    dst_file = os.path.join("public_staging", "panorama-market-share", "index.html")

    with open(src_file, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # 1. Separar estilos, corpo e scripts
    style_match = re.search(r'<style>(.*?)</style>', content, re.DOTALL)
    script_idx = content.find('<script')
    body_start_idx = content.find('<body>')
    
    html_body = content[body_start_idx:script_idx]
    scripts_part = content[script_idx:]

    # 2. Novo CSS Oficial Churn Safra
    churn_css = """
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
  --amber: #c98a15;
  --green: #2f7d5d;
  --blue: #2a5d8f;
  --purple: #6b4b8a;
  --dark: #1b2430;
  --slate: #1c2430;
  --muted: #5b6675;
  --isp: #5b6675;
  --gold: #c98a15;
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
.kpi { padding: 12px 14px; border-right: 1px solid var(--line2); }
.kpi:last-child { border-right: none; }
.kpi .k { font-size: 10.5px; text-transform: uppercase; letter-spacing: .5px; color: var(--ink3); font-weight: 600; }
.kpi .v, .kpi b { font-size: 22px !important; font-weight: 600; margin-top: 3px; letter-spacing: -.3px; color: var(--ink); display: block; line-height: 1.1; }
.kpi .d, .kpi i { font-size: 11px; color: var(--ink2); margin-top: 2px; font-style: normal; display: block; }
.kpi.acc .v, .down { color: var(--red) !important; }
.kpi.good .v, .up { color: var(--green) !important; }

/* Filtros Globais */
.filters-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 10px; }
.f-box { border: 1px solid var(--line2); border-radius: 3px; padding: 7px 8px 8px; background: #fcfcfd; }
.f-box label { display: block; font-size: 10.5px; text-transform: uppercase; letter-spacing: .5px; color: var(--ink3); margin-bottom: 4px; font-weight: 700; }
.f-box select, .f-box input { width: 100%; border: 1px solid var(--line); border-radius: 2px; padding: 4px 6px; font: 12px "Segoe UI", Arial; color: var(--ink); background: #fff; outline: none; }
.f-box select:focus, .f-box input:focus { border-color: var(--blue); }
.drawer-btn {
  display: inline-flex; align-items: center; gap: 7px; background: var(--nav); color: #fff; border: 1px solid var(--nav);
  border-radius: 2px; font-size: 11.5px; font-weight: 600; text-transform: uppercase; letter-spacing: .5px; padding: 5px 12px; cursor: pointer;
}
.drawer-btn:hover { background: var(--nav2); }

/* Tabelas Analíticas Churn Safra */
.tblwrap, .tablewrap { overflow-x: auto; border: 1px solid var(--line2); border-radius: 3px; background: #fff; }
table { width: 100%; border-collapse: collapse; font-size: 12px; }
th, td { padding: 6px 8px; border-bottom: 1px solid var(--line2); text-align: right; white-space: nowrap; }
th { background: #f7f8fa; color: var(--ink2); font-weight: 600; font-size: 10.5px; text-transform: uppercase; letter-spacing: .3px; position: sticky; top: 0; z-index: 2; border-bottom: 1px solid var(--line); }
th.l, td.l, td.praca { text-align: left; }
tbody tr:hover { background: #f7f9fb; }
tr.total td { background: #eef1f6; font-weight: 700; border-top: 2px solid var(--line); border-bottom: 2px solid var(--line); }
tr.cab td { background: #fffcf5; }
.sortable { cursor: pointer; user-select: none; }
.sortable:after { content: " ▾"; opacity: .4; }

/* Badges e Posições Sóbrias */
.pos { display: inline-block; padding: 2px 7px; border-radius: 2px; font-size: 11px; font-weight: 700; }
.pos.p1, .lead.win { background: #eaf2ec; color: var(--green); }
.pos.p2 { background: #fdf3e2; color: var(--amber); }
.pos.p3, .lead.isp { background: #f0f2f5; color: var(--ink2); }
.pos.px, .lead.lose { background: #fdece9; color: var(--red); }
.lead { display: inline-flex; align-items: center; gap: 4px; padding: 2px 7px; border-radius: 2px; font-size: 11px; font-weight: 700; }

.dnum { display: inline-block; background: var(--nav); color: #fff; font-weight: 700; border-radius: 2px; padding: 1px 5px; font-size: 10.5px; margin-right: 5px; }
.rno-ic { background: var(--red); }
.cabflag { display: inline-block; background: var(--amber); color: #fff; font-size: 8.5px; font-weight: 700; border-radius: 2px; padding: 1px 4px; margin-left: 4px; }
.ci { font-size: 10px; color: var(--ink3); margin-top: 1px; }

/* Barras de Share em Tabelas */
.bar { display: flex; height: 16px; border-radius: 2px; overflow: hidden; background: #eceef1; min-width: 180px; }
.bar span { display: flex; align-items: center; height: 100%; font-size: 9.5px; color: #fff; font-weight: 700; padding-left: 3px; overflow: hidden; }

/* Gráficos e SVG Responsivos com Halo Branco */
svg text {
  font-family: "Segoe UI", Roboto, Arial, sans-serif !important;
  paint-order: stroke fill;
  stroke: #fff;
  stroke-width: 2.5px;
}
.gtip { position: absolute; z-index: 100; pointer-events: none; background: rgba(27,36,48,.94); color: #fff; font-size: 11.5px; padding: 6px 10px; border-radius: 3px; }

/* Mapa com Fundo Neutro */
.mapbox { position: relative; background: #eef1f3; border: 1px solid var(--line2); border-radius: 3px; overflow: hidden; padding: 8px; }
.mapbox svg { width: 100%; height: auto; display: block; max-height: 75vh; }
.maplegend { display: flex; gap: 14px; flex-wrap: wrap; font-size: 11px; margin: 8px 0; align-items: center; color: var(--ink2); }

/* Chips e Botões */
.tag2 { background: #eef1f6; border: 1px solid var(--line); border-radius: 2px; padding: 2px 7px; font-size: 11px; font-weight: 600; color: var(--ink2); display: inline-flex; align-items: center; gap: 5px; }
.tag2 b { color: var(--red); }
.simbtn { border: 1px solid var(--line); background: #fff; color: var(--ink); padding: 3px 8px; border-radius: 2px; font-size: 11px; font-weight: 600; cursor: pointer; }
.simbtn:hover { background: #f0f2f5; border-color: var(--blue); }
"""

    # 3. Reescrever o cabeçalho e estrutura do body
    # Substituir cover, nav antigo e filterbar antiga por componentes Churn Safra
    clean_body = """
<body>

<!-- Header Corporativo Oficial Claro PEP HUB -->
<header>
  <div class="hd-bar">
    <div class="hd-ico">
      <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="10"/><path d="M2 12h20"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
      </svg>
    </div>
    <h1>
      <b>Panorama de Market Share</b>
      <span>Móvel & Banda Larga Residencial · Regional Norte</span>
    </h1>
    <a href="/" class="back-hub" style="margin-left:auto;">‹ Portal Pephub</a>
  </div>
  <div class="hd-sub">
    <span><b>Panorama de Market Share</b></span>
    <span class="dot"></span>
    <span>Posição Oficial: <b>Jul/2026 (Base Anatel)</b></span>
    <span class="dot"></span>
    <span>Regional Norte (AM · AP · MA · PA · PI · RR)</span>
    <span class="dot"></span>
    <span>Escopo: <b>Móvel & Banda Larga Fixa</b></span>
    <div class="hd-right">
      <span>Planejamento & Performance</span>
    </div>
  </div>
</header>

<div class="wrap">

  <!-- Painel de Navegação Executiva (Tabs Churn Safra) -->
  <div class="panel" style="margin-bottom:14px;">
    <h2>NAVEGAÇÃO EXECUTIVA <span class="note">Cortes analíticos, mapas e cruzamentos de convergência</span></h2>
    <div class="pbody" style="padding:8px 14px;">
      <nav class="tabs" style="margin-left:0;">
        <a href="#resumo" class="on">Resumo Executivo</a>
        <a href="#mapa">Mapa de Liderança</a>
        <a href="#movel">Móvel por Produto</a>
        <a href="#residencial">Banda Larga Residencial</a>
        <a href="#isp">ISPs Individualizados</a>
        <a href="#comparador">Comparador Claro × Concorrente</a>
        <a href="#cruzamento">Cruzamentos Móvel × Fixa</a>
        <a href="#oportunidades">Oportunidades de Convergência</a>
        <a href="#metodo">Metodologia</a>
      </nav>
    </div>
  </div>

  <!-- Painel de Filtros Globais (Churn Safra Pattern) -->
  <div class="panel">
    <h2>FILTROS GLOBAIS <span class="note">Filtre por Estado, DDD, Município, Escopo e Tipo de Pessoa</span> <button class="drawer-btn" style="margin-left:auto;" onclick="document.getElementById('fbody').classList.toggle('collapsed')">Filtros</button> <button class="hlp" data-h="filtros">?</button></h2>
    <div class="pbody" id="fbody">
      <div class="filterbar" style="border:none; box-shadow:none; padding:0; position:static;">
        <div class="wrap" style="padding:0; gap:8px;">
          <!-- Filtros preservados para manter reatividade total dos scripts -->
          <div class="ms" id="msUf"><button type="button">UF <span class="cnt" style="display:none">0</span><span class="cx">▾</span></button><div class="panel" style="display:none"><input class="srch" placeholder="Buscar UF..."><div class="opts"></div></div></div>
          <div class="ms" id="msDdd"><button type="button">DDD <span class="cnt" style="display:none">0</span><span class="cx">▾</span></button><div class="panel" style="display:none"><input class="srch" placeholder="Buscar DDD..."><div class="opts"></div></div></div>
          <div class="ms" id="msMun"><button type="button">Município <span class="cnt" style="display:none">0</span><span class="cx">▾</span></button><div class="panel" style="display:none"><input class="srch" placeholder="Buscar município..."><div class="opts"></div></div></div>
          
          <div class="seg-pills" id="segZona">
            <button class="on" data-z="ALL">Todas as Cidades</button>
            <button data-z="RNO">Apenas RNO Oficial</button>
            <button data-z="CAB">Cidades Cabeadas Claro</button>
          </div>

          <div class="seg-pills" id="segPess">
            <button class="on" data-p="ALL">PF + PJ</button>
            <button data-p="PF">Pessoa Física</button>
            <button data-p="PJ">Pessoa Jurídica</button>
          </div>

          <div class="tags" id="activeTags"></div>
          <button class="clearall" id="btnClearAll" style="margin-left:auto; display:none;">Limpar filtros</button>
        </div>
      </div>
    </div>
  </div>
"""

    # 4. Transformar todas as seções em Painéis .panel no corpo
    # Extrair apenas o miolo das seções existentes a partir de <section id="resumo">
    sec_start = html_body.find('<section id="resumo"')
    if sec_start == -1:
        sec_start = html_body.find('<section')
    
    sections_content = html_body[sec_start:]
    
    # Substituir <section id="..."> por <div class="panel" id="...">
    sections_content = re.sub(r'<section\s+id=["\']([^"\']+)["\'][^>]*>', r'<div class="panel" id="\1">', sections_content)
    sections_content = sections_content.replace('</section>', '</div></div>') # fecha pbody e panel

    # Transformar <h2>Título</h2> em <h2>TÍTULO <span class="note">...</span> <button class="hlp">?</button></h2><div class="pbody">
    def h2_repl(m):
        raw_h2 = m.group(1).strip()
        clean_title = re.sub(r'<[^>]+>', '', raw_h2).strip().upper()
        # atribuir helper correspondente
        h_key = "resumo"
        if "MAPA" in clean_title: h_key = "mapa"
        elif "MÓVEL" in clean_title: h_key = "movel"
        elif "RESIDENCIAL" in clean_title or "BANDA LARGA" in clean_title: h_key = "residencial"
        elif "ISP" in clean_title: h_key = "isp"
        elif "COMPARADOR" in clean_title: h_key = "comparador"
        elif "CRUZAMENTO" in clean_title or "DISPERS" in clean_title: h_key = "scatter"
        elif "OPORTUNIDADE" in clean_title: h_key = "oportunidades"
        elif "METODOLOGIA" in clean_title: h_key = "metodo"
        
        return f'<h2>{clean_title} <span class="note">Acompanhamento executivo da Regional Norte</span> <button class="hlp" data-h="{h_key}">?</button></h2>\n<div class="pbody">'

    sections_content = re.sub(r'<h2>(.*?)</h2>', h2_repl, sections_content)

    # Limpar emojis informais de todo o HTML de seções
    emoji_cleanups = [
        ("🔎 detalhes", "Detalhes"),
        ("📈 Simular", "Simular"),
        ("🧭 Sociodemográfico", "Sociodemográfico"),
        ("📊 Mercado fixo", "Mercado fixo"),
        ("💰 Renda & consumo", "Renda & consumo"),
        ("📱 Móvel — Claro × Vivo", "Móvel — Claro × Vivo"),
        ("📶 Qualidade fixa", "Qualidade fixa"),
        ("🏗️ Construção civil", "Construção civil"),
        ("🏗 Construção civil", "Construção civil"),
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
    for old, new in emoji_cleanups:
        sections_content = sections_content.replace(old, new)

    # 5. Adicionar HELP dictionary no script
    help_script = """
<script>
const HELP = {
  filtros: "Filtros multidimensionais que restringem a base por UF, DDD, Município, Escopo geográfico e Natureza jurídica (PF/PJ).",
  resumo: "Síntese executiva do volume total de acessos, adição líquida e posição da Claro versus concorrentes na Regional Norte.",
  mapa: "Distribuição espacial dos municípios da Regional Norte indicando a operadora líder em cada mercado local.",
  movel: "Abertura do segmento móvel entre pré-pago, pós-pago e tecnologias celulares.",
  residencial: "Desempenho da banda larga fixa residencial, net adds e evolução da base instalada.",
  isp: "Ranking e perfil dos provedores regionais de internet (ISPs) individualizados por praça.",
  comparador: "Confronto direto e cálculo do diferencial competitivo entre Claro e a operadora selecionada.",
  scatter: "Matriz de dispersão e correlação entre penetração móvel e cobertura de banda larga fixa.",
  oportunidades: "Mapeamento de praças com maior potencial para expansão de rede e conversão de base convergente.",
  metodo: "Notas metodológicas, critérios da Anatel e periodicidade dos dados consolidados."
};
document.addEventListener('click', function(e) {
  if (e.target && e.target.classList && e.target.classList.contains('hlp')) {
    const key = e.target.getAttribute('data-h');
    if (HELP[key]) alert(HELP[key]);
  }
});
</script>
"""

    # Montar arquivo final
    final_html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Panorama Market Share — Móvel & Residencial · Regional Norte</title>
<style>
{churn_css}
</style>
</head>
{clean_body}
{sections_content}
</div> <!-- fim .wrap -->

{scripts_part}
{help_script}
</body>
</html>
"""

    # Limpar emojis informais de todo o conteúdo (inclusive scripts)
    informal_emoji_re = re.compile(
        r'[\U0001F600-\U0001F64F]|[\U0001F300-\U0001F5FF]|[\U0001F680-\U0001F6FF]|[\U0001F900-\U0001F9FF]|[\U0001FA70-\U0001FAFF]'
    )
    final_html = informal_emoji_re.sub('', final_html)

    # Garantir que a seção de dispersão tem o helper correto
    if 'data-h="scatter"' not in final_html:
        final_html = final_html.replace('CRUZAMENTOS MÓVEL', 'CRUZAMENTOS MÓVEL <button class="hlp" data-h="scatter">?</button>')

    with open(dst_file, "w", encoding="utf-8") as f:
        f.write(final_html)

    print(f"✅ Panorama Market Share reconstruído com sucesso no padrão Churn Safra em {dst_file}")

if __name__ == "__main__":
    rebuild_panorama()
