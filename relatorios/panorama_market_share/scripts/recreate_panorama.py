import re

# Read from the original source file to ensure pristine data extraction
with open('Panorama_MktShare_Movel_Residencial_RNO_jul26 10.html', 'r', encoding='utf-8') as f:
    orig_content = f.read()

# Extract script blocks
scripts = re.findall(r'<script[^>]*>(.*?)</script>', orig_content, re.DOTALL)
if len(scripts) < 2:
    raise ValueError("Could not find the expected script blocks in original panorama market share file!")

data_script = scripts[0]  # const DATA = ...
engine_script = scripts[1] # functions and engine

# Polish functions in engine_script
# 1. Update meta()
engine_script = re.sub(
    r'function meta\(t,v\)\{return `[^`]+`\}',
    'function meta(t,v){return `<div class="kpi"><span class="k">${t}</span><b class="v">${v}</b><span class="d">Regional Norte</span></div>`}',
    engine_script
)

# 2. Update rc()
engine_script = re.sub(
    r'function rc\(t,v,c,sub\)\{return `[^`]+`\}',
    'function rc(t,v,c,sub){return `<div class="kpi"><span class="k">${t}</span><b class="v" style="color:${c}">${v}</b><span class="d">${sub}</span></div>`}',
    engine_script
)

# 3. Update kpi()
engine_script = re.sub(
    r'function kpi\(t,v,sub,up,cls\)\{let vc=cls===\'cab\'\?\'style="color:var\(--gold\)"\':\'\';let ic=sub\?`<i class="\$\{up===true\?\'up\':up===false\?\'down\':\'\'\}">\$\{sub\}</i>`:\'\';return `<div class="kpi"><span>\$\{t\}</span><b \$\{vc\}>\$\{v\}</b>\$\{ic\}</div>`\}',
    'function kpi(t,v,sub,up,cls){let vc=cls===\'cab\'?\'style="color:var(--amber)"\':\'\';let ic=sub?`<span class="d ${up===true?\'up\':up===false?\'down\':\'\'}">${sub}</span>`:\'\';return `<div class="kpi"><span class="k">${t}</span><b class="v" ${vc}>${v}</b>${ic}</div>`}',
    engine_script
)

# 4. Enhance trendSpark so sparklines scale visibly across data range
new_spark = """function trendSpark(vals,color){
  const w=180,h=36;
  const validVals=vals.filter(v=>typeof v==='number'&&!isNaN(v));
  if(!validVals.length) return '';
  const mx=Math.max(...validVals), mn=Math.min(...validVals);
  const spread=(mx-mn)||Math.max(mx*0.05, 1);
  const yMin=Math.max(0, mn - spread*0.25), yMax=mx + spread*0.25;
  const X=i=>(i/(vals.length-1||1))*(w-16)+8;
  const Y=v=>Math.max(4, Math.min(h-4, h - 4 - ((v-yMin)/((yMax-yMin)||1))*(h-8)));
  const d=vals.map((v,i)=>`${i?'L':'M'}${X(i).toFixed(1)},${Y(v).toFixed(1)}`).join(' ');
  const lastPt=vals[vals.length-1];
  return `<svg viewBox="0 0 ${w} ${h}" style="width:${w}px;height:${h}px;display:block;margin-top:4px;background:#f9fafb;border-radius:2px;border:1px solid var(--line2)">
    <path d="${d}" fill="none" stroke="${color}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
    ${vals.map((v,i)=>`<circle cx="${X(i).toFixed(1)}" cy="${Y(v).toFixed(1)}" r="2.5" fill="${color}"/>`).join('')}
  </svg>`;
}"""
engine_script = re.sub(r'function trendSpark\(vals,color\)\{[\s\S]*?<\/svg>`;\n\}', new_spark, engine_script)

# 5. Clean emojis in text and templates within engine_script
emoji_subs = [
    ("\U0001f4c8 Simulador", "Simulador"),
    ("\U0001f50e detalhes", "detalhes"),
    ("📊 Sociodemográfico (IBGE)", "Sociodemográfico (IBGE)"),
    ("📶 Mercado fixo (base do estudo)", "Mercado Fixo"),
    ("💰 Renda & consumo", "Renda & Consumo"),
    ("📱 Móvel — Claro × Vivo", "Móvel — Claro × Concorrente"),
    ("🌐 Qualidade fixa (IQC · Selo · SIMET)", "Qualidade Fixa (IQC · Selo · SIMET)"),
    ("🏗️ Construção civil (CNO)", "Construção Civil (CNO)"),
    ("ℹ️ Cobertura de dados", "Cobertura de Dados"),
    ("✅ carregado", "Carregado (IBGE Oficial)"),
    ("✅ Radar/Anatel", "Radar da Telecom / Anatel"),
    ("🧭", ""),
    ("📊", ""),
    ("📶", ""),
    ("💰", ""),
    ("📱", ""),
    ("🏗️", ""),
    ("ℹ️", ""),
    ("✅", ""),
]
for old_e, new_e in emoji_subs:
    engine_script = engine_script.replace(old_e, new_e)

css_content = """
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

/* Botoes de Acao Superior Direito (Padrao FPD / Safra) */
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
  margin-left: auto; display: inline-flex; align-items: center; gap: 5px;
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

/* Abas de Navegacao Executiva */
.tabs { display: flex; gap: 6px; flex-wrap: wrap; align-items: center; }
.tabs a, .tabs button {
  border: 1px solid var(--line); background: #fff; color: var(--ink);
  font-size: 11.5px; padding: 6px 14px; border-radius: 2px; text-decoration: none;
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
.kpi { padding: 10px 14px; border-right: 1px solid var(--line2); border-bottom: 1px solid var(--line2); }
.kpi:last-child { border-right: none; }
.kpi .k { font-size: 10.5px; text-transform: uppercase; letter-spacing: .5px; color: var(--ink3); font-weight: 600; display: block; }
.kpi .v, .kpi b { font-size: 22px !important; font-weight: 600; margin-top: 3px; letter-spacing: -.3px; color: var(--ink); display: block; line-height: 1.1; }
.kpi .d, .kpi i { font-size: 11px; color: var(--ink2); margin-top: 2px; font-style: normal; display: block; }
.kpi.acc .v, .down { color: var(--red) !important; }
.kpi.good .v, .up { color: var(--green) !important; }

/* Filtros Globais */
.filters-row { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.fl-lbl { font-size: 10.5px; font-weight: 700; text-transform: uppercase; letter-spacing: .5px; color: var(--ink3); margin-right: 2px; }

.ms { position: relative; display: inline-block; }
.ms > button {
  border: 1px solid var(--line); background: #fff; border-radius: 2px;
  padding: 5px 11px; font: 600 11.5px "Segoe UI", Arial, sans-serif; color: var(--ink);
  cursor: pointer; display: inline-flex; align-items: center; gap: 6px; white-space: nowrap; height: 30px;
  transition: background .15s, border-color .15s;
}
.ms > button:hover { background: #f0f2f5; border-color: var(--nav); }
.ms > button .cnt { background: var(--red); color: #fff; border-radius: 999px; font-size: 9.5px; padding: 1px 5px; font-weight: 700; }
.ms > button .cx { color: var(--ink3); font-size: 10px; margin-left: 2px; }
.ms > .panel {
  position: absolute; top: calc(100% + 4px); left: 0; background: #fff;
  border: 1px solid var(--line); border-radius: 3px; box-shadow: 0 8px 24px rgba(0,0,0,.15);
  padding: 8px; min-width: 230px; max-height: 320px; overflow-y: auto; display: none; z-index: 200; margin: 0;
}
.ms.open > .panel { display: block; }
.ms > .panel input.srch {
  width: 100%; border: 1px solid var(--line); border-radius: 2px; padding: 5px 8px;
  font: 11.5px "Segoe UI", Arial; margin-bottom: 6px; outline: none; box-sizing: border-box;
}
.ms > .panel input.srch:focus { border-color: var(--blue); }
.ms .opts { max-height: 220px; overflow-y: auto; }
.ms .opt { display: flex; align-items: center; gap: 6px; padding: 4px 6px; border-radius: 2px; font-size: 11.5px; cursor: pointer; color: var(--ink); }
.ms .opt:hover { background: #f0f2f5; }
.ms .opt input { accent-color: var(--red); }

.seg-pills { display: inline-flex; border: 1px solid var(--line); border-radius: 2px; overflow: hidden; background: #fff; height: 30px; }
.seg-pills button {
  border: none; border-right: 1px solid var(--line2); background: #fff; color: var(--ink2);
  padding: 0 12px; font: 600 11.5px "Segoe UI", Arial, sans-serif; cursor: pointer; line-height: 28px;
  transition: background .15s, color .15s;
}
.seg-pills button:last-child { border-right: none; }
.seg-pills button:hover { background: #f0f2f5; color: var(--ink); }
.seg-pills button.on { background: var(--nav) !important; color: #fff !important; font-weight: 700; }

.tags { display: flex; gap: 6px; flex-wrap: wrap; align-items: center; }
.tag2 {
  background: #eef1f6; border: 1px solid var(--line); border-radius: 2px; padding: 2px 7px;
  font-size: 11px; font-weight: 600; color: var(--ink2); display: inline-flex; align-items: center; gap: 5px;
}
.tag2 b { color: var(--red); }
.tag2 .x { cursor: pointer; color: var(--ink3); font-weight: 700; font-size: 11px; margin-left: 2px; }
.tag2 .x:hover { color: var(--red); }
.clearall {
  font-size: 11.5px; color: var(--red); cursor: pointer; font-weight: 600;
  border: 1px solid transparent; background: none; padding: 3px 6px; border-radius: 2px;
}
.clearall:hover { text-decoration: underline; }

/* Controles de Segmento (sgt) e Toggles */
.sgt-wrap { display: flex; gap: 4px; flex-wrap: wrap; margin-bottom: 12px; }
.sgt {
  border: 1px solid var(--line); background: #fff; color: var(--ink); padding: 5px 12px;
  border-radius: 2px; font: 600 11.5px "Segoe UI", Arial, sans-serif; cursor: pointer;
  transition: background .15s, border-color .15s;
}
.sgt:hover { background: #f0f2f5; border-color: var(--nav); }
.sgt.on { background: var(--nav) !important; color: #fff !important; border-color: var(--nav) !important; font-weight: 700; }

.toggle { display: inline-flex; border: 1px solid var(--line); border-radius: 2px; overflow: hidden; background: #fff; height: 28px; }
.toggle button {
  border: none; border-right: 1px solid var(--line2); background: #fff; color: var(--ink2);
  padding: 0 11px; font: 600 11.5px "Segoe UI", Arial, sans-serif; cursor: pointer; line-height: 26px;
}
.toggle button:last-child { border-right: none; }
.toggle button:hover { background: #f0f2f5; color: var(--ink); }
.toggle button.on { background: var(--nav) !important; color: #fff !important; font-weight: 700; }

/* Tabelas Analiticas */
.tblwrap, .tablewrap { overflow-x: auto; border: 1px solid var(--line2); border-radius: 3px; background: #fff; margin-top: 8px; }
table { width: 100%; border-collapse: collapse; font-size: 12px; }
th, td { padding: 6px 8px; border-bottom: 1px solid var(--line2); text-align: right; white-space: nowrap; }
th {
  background: #f7f8fa; color: var(--ink2); font-weight: 600; font-size: 10.5px;
  text-transform: uppercase; letter-spacing: .3px; position: sticky; top: 0; z-index: 2; border-bottom: 1px solid var(--line);
}
th.l, td.l, td.praca { text-align: left; }
tbody tr:hover { background: #f7f9fb; }
tr.total td { background: #eef1f6; font-weight: 700; border-top: 2px solid var(--line); border-bottom: 2px solid var(--line); }
tr.cab td { background: #fffcf5; }
tr.found td { background: #f0f7ff; }

/* Badges e Posicoes */
.pos { display: inline-block; padding: 2px 7px; border-radius: 2px; font-size: 11px; font-weight: 700; }
.pos.p1, .lead.win { background: #eaf2ec; color: var(--green); }
.pos.p2 { background: #fdf3e2; color: var(--amber); }
.pos.p3, .lead.isp { background: #f0f2f5; color: var(--ink2); }
.pos.px, .lead.lose { background: #fdece9; color: var(--red); }
.lead { display: inline-flex; align-items: center; gap: 4px; padding: 2px 7px; border-radius: 2px; font-size: 11px; font-weight: 700; white-space: nowrap; }

.dnum { display: inline-block; background: var(--nav); color: #fff; font-weight: 700; border-radius: 2px; padding: 1px 5px; font-size: 10.5px; margin-right: 5px; }
.rno-ic { background: var(--red); }
.cabflag { display: inline-block; background: var(--amber); color: #fff; font-size: 8.5px; font-weight: 700; border-radius: 2px; padding: 1px 4px; margin-left: 4px; }
.ci { font-size: 10px; color: var(--ink3); margin-top: 1px; display: block; }

/* Barras de Share e Graficos */
.bar { display: flex; height: 16px; border-radius: 2px; overflow: hidden; background: #eceef1; min-width: 180px; }
.bar span { display: flex; align-items: center; height: 100%; font-size: 9.5px; color: #fff; font-weight: 700; padding-left: 3px; overflow: hidden; }

svg text {
  font-family: "Segoe UI", Roboto, Arial, sans-serif !important;
  paint-order: stroke fill; stroke: #fff; stroke-width: 2.5px;
}
.scatter { width: 100%; height: auto; background: #fff; border: 1px solid var(--line2); border-radius: 3px; }

/* Mapa */
.mapbox { position: relative; background: #eef1f3; border: 1px solid var(--line2); border-radius: 3px; overflow: hidden; padding: 8px; }
.mapbox svg { width: 100%; height: auto; display: block; max-height: 75vh; }
.mapbox svg path { stroke: #fff; stroke-width: .35; cursor: pointer; transition: opacity .1s; }
.mapbox svg path:hover { opacity: .75; stroke: var(--nav); stroke-width: .85; }
.mapbox svg path.cab { stroke: #B98900; stroke-width: 1; }
.maplegend { display: flex; gap: 14px; flex-wrap: wrap; font-size: 11px; margin: 8px 0; align-items: center; color: var(--ink2); }
.maplegend span { display: flex; align-items: center; gap: 6px; }
.maplegend i { width: 11px; height: 11px; border-radius: 2px; display: inline-block; }
.maptip {
  position: absolute; display: none; z-index: 150; background: rgba(20,27,36,.96);
  border: 1px solid var(--line); border-radius: 3px; color: #fff; padding: 10px 12px; width: 260px;
  pointer-events: none; font-size: 11.5px; box-shadow: 0 8px 24px rgba(0,0,0,.25);
}
.maptip .tiphead { font-weight: 700; font-size: 12px; margin-bottom: 6px; color: #fff; }
.maptip .pbrow { margin: 4px 0; }
.maptip .pblbl { font-size: 10px; font-weight: 700; text-transform: uppercase; color: #aab4c0; }
.maptip .pbline { display: flex; align-items: center; gap: 6px; margin: 2px 0; }
.maptip .pbname { width: 44px; font-size: 10px; text-align: right; color: #dbe2ec; flex: none; }
.maptip .pbtrack { flex: 1; background: rgba(255,255,255,.2); height: 8px; border-radius: 2px; overflow: hidden; }
.maptip .pbfill { height: 100%; }
.maptip .pbval { width: 38px; font-size: 10px; font-weight: 700; text-align: right; flex: none; }
.maptip .tipna { margin-top: 6px; padding-top: 6px; border-top: 1px solid rgba(255,255,255,.18); font-size: 10px; color: #aab4c0; }

/* Galeria de Players */
.pgallery { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; }
.gchip {
  display: flex; align-items: center; gap: 6px; border: 1px solid var(--line); background: #fff;
  border-radius: 2px; padding: 4px 10px; font-size: 11.5px; font-weight: 600; color: var(--ink);
  cursor: pointer; transition: all .12s;
}
.gchip:hover { background: var(--nav); color: #fff; border-color: var(--nav); }

/* Comparador */
.selrow { display: flex; gap: 10px; flex-wrap: wrap; align-items: center; margin-bottom: 12px; }
.selrow select {
  border: 1px solid var(--line); border-radius: 2px; padding: 5px 10px; font: 600 12px "Segoe UI", Arial;
  color: var(--ink); background: #fff; min-width: 180px; height: 30px; outline: none;
}
.vs {
  display: grid; grid-template-columns: 1fr 60px 1fr; background: #fff;
  border: 1px solid var(--line); border-radius: 3px; overflow: hidden;
}
.vs .side { padding: 18px 22px; }
.vs .side.a { background: #fffcfc; border-right: 1px solid var(--line2); }
.vs .side.b { background: #fafbfe; border-left: 1px solid var(--line2); }
.vs .mid {
  background: var(--nav); color: #fff; display: flex; align-items: center;
  justify-content: center; font-weight: 800; font-size: 14px; letter-spacing: 1px;
}
.vs h4 { font-size: 18px; font-weight: 700; margin-bottom: 2px; }
.vs .rowm {
  display: flex; justify-content: space-between; align-items: center;
  padding: 8px 0; border-bottom: 1px solid var(--line2); font-size: 12.5px;
}
.vs .rowm:last-child { border-bottom: none; }
.vs .rowm .k { color: var(--ink3); font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: .4px; }
.vs .rowm .v { font-size: 16px; font-weight: 700; }
.vs .win { color: var(--green) !important; }
.vs .lose { color: var(--red) !important; }

/* Cards Genericos e Grids */
.card { background: #fff; border: 1px solid var(--line); border-radius: 3px; padding: 14px; }
.grid { display: grid; gap: 12px; }
.g2 { grid-template-columns: 1fr 1fr; }
.g3 { grid-template-columns: repeat(3, 1fr); }
.g4 { grid-template-columns: repeat(4, 1fr); }
.g5 { grid-template-columns: repeat(5, 1fr); }
@media(max-width: 1000px) { .g5, .g4, .g3, .g2, .vs { grid-template-columns: 1fr; } .vs .mid { padding: 6px; } }

.lead-txt { font-size: 13px; color: var(--ink2); margin-bottom: 12px; line-height: 1.5; }
.note { font-size: 11px; color: var(--ink3); font-style: normal; margin-top: 6px; }
.dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; vertical-align: middle; margin-right: 4px; }
.chips { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 10px; }
.citychip {
  background: #fffcf5; color: var(--amber); border: 1px solid #f0dcb4; border-radius: 2px;
  padding: 3px 8px; font-size: 11px; font-weight: 600;
}
.citychip b { color: var(--ink); margin-left: 2px; }

/* ISP Bars */
.ispbar { display: flex; align-items: center; gap: 10px; margin: 6px 0; }
.ispbar .nm { width: 170px; font-size: 11.5px; font-weight: 600; color: var(--ink); text-align: right; flex: none; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.ispbar .tr { flex: 1; background: #eef1f5; border-radius: 2px; height: 18px; overflow: hidden; }
.ispbar .fl { height: 100%; display: flex; align-items: center; padding-left: 8px; color: #fff; font-size: 10.5px; font-weight: 700; }
.ispbar .vv { width: 110px; font-size: 11px; color: var(--ink3); flex: none; }

/* Recomendacoes Estrategicas (.ins) */
.ins {
  border: 1px solid var(--line); border-left: 4px solid var(--red); border-radius: 2px;
  background: #fff; padding: 10px 14px; margin: 8px 0;
}
.ins h4 { margin: 0 0 4px; font-size: 12px; font-weight: 700; color: var(--ink); }
.ins p { margin: 0; font-size: 12px; color: var(--ink2); line-height: 1.5; }

.tag { display: inline-block; font-size: 10.5px; font-weight: 700; padding: 2px 7px; border-radius: 2px; }
.tag.opp { background: #eaf2ec; color: var(--green); border: 1px solid #c9dfd2; }
.tag.watch { background: #fdf3e2; color: var(--amber); border: 1px solid #f0dcb4; }
.tag.risk { background: #fdece9; color: var(--red); border: 1px solid #f6c8c2; }

/* Simulador Button & Controls */
.simbtn {
  border: 1px solid var(--line); background: #fff; color: var(--ink);
  border-radius: 2px; padding: 3px 8px; font-size: 11px; font-weight: 600; cursor: pointer; white-space: nowrap;
}
.simbtn:hover { background: #f0f2f5; border-color: var(--blue); color: var(--blue); }

.simctl { background: #fafbfc; border: 1px solid var(--line); border-radius: 3px; padding: 12px 14px; margin-bottom: 12px; }
.simctl label { font-size: 12px; font-weight: 700; color: var(--ink); display: block; margin-bottom: 6px; }
.simctl input[type=range] { width: 100%; accent-color: var(--red); margin: 6px 0; }
.simquick { display: flex; gap: 4px; flex-wrap: wrap; margin-top: 6px; }
.simquick button {
  border: 1px solid var(--line); background: #fff; border-radius: 2px; padding: 3px 8px;
  font-size: 11px; font-weight: 600; cursor: pointer; color: var(--ink2);
}
.simquick button:hover { background: var(--nav); color: #fff; border-color: var(--nav); }
.simadds { margin-top: 8px; font-size: 12px; color: var(--ink); display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.simadds .arrow { color: var(--red); font-weight: 700; }

/* Gap steps (Milestones no Simulador) */
.gaptitle { font-size: 12px; font-weight: 700; color: var(--ink); margin: 14px 0 8px; text-transform: uppercase; letter-spacing: .4px; }
.gapsteps { display: grid; grid-template-columns: repeat(auto-fit, minmax(95px, 1fr)); gap: 8px; margin-bottom: 14px; width: 100%; box-sizing: border-box; }
.gapstep {
  background: #f7f9fb; border: 1px solid var(--line); border-radius: 3px;
  padding: 8px 10px; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,.04); box-sizing: border-box;
}
.gapstep.closed { background: #eaf2ec; border-color: #c9dfd2; }
.gapstep .gm { font-size: 10.5px; color: var(--ink3); font-weight: 700; text-transform: uppercase; }
.gapstep .gv { font-size: 13px; font-weight: 700; color: var(--ink); margin: 3px 0 6px; font-variant-numeric: tabular-nums; }
.gapstep.closed .gv { color: var(--green); font-size: 11px; }
.gapstep .gbarwrap { background: #dfe3e8; border-radius: 2px; height: 5px; overflow: hidden; margin-top: 4px; }
.gapstep .gbar { height: 100%; background: linear-gradient(90deg, var(--red), var(--green)); }

.gapcell { font-size: 11px; line-height: 1.3; text-align: left; min-width: 140px; white-space: normal; }
.gapcell .g1 { font-weight: 700; color: var(--ink); }
.gapcell .g2 { color: var(--ink2); }
.gapcell .fast { color: var(--green); font-weight: 700; }
.gapcell .slow { color: var(--red); font-weight: 700; }

/* Modal */
#modalRoot .modal-bg {
  position: fixed; inset: 0; background: rgba(18,24,32,.55); z-index: 300;
  display: flex; align-items: flex-start; justify-content: center; padding: 34px 16px; overflow-y: auto;
}
#modalRoot .modal {
  background: #fff; border-radius: 4px; max-width: 900px; width: 100%; padding: 22px;
  position: relative; box-shadow: 0 14px 48px rgba(0,0,0,.3); border: 1px solid var(--line);
}
#modalRoot .modal-x {
  position: absolute; top: 12px; right: 14px; border: 1px solid var(--line);
  background: #fff; border-radius: 50%; width: 26px; height: 26px; font-size: 14px;
  cursor: pointer; color: var(--ink3); display: flex; align-items: center; justify-content: center;
}
#modalRoot .modal-x:hover { background: var(--nav); color: #fff; border-color: var(--nav); }

table.mini { width: 100%; border-collapse: collapse; font-size: 11.5px; }
table.mini td { padding: 4px 6px; border-bottom: 1px solid var(--line2); }
table.mini td.k { color: var(--ink3); font-weight: 600; }
table.mini td.v { text-align: right; font-weight: 700; }

footer {
  border-top: 1px solid var(--line2); padding: 24px 0 10px; font-size: 11.5px; color: var(--ink3);
  margin-top: 24px; text-align: center; line-height: 1.6;
}
footer b { color: var(--ink2); }
"""

html_body = """
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
    <div class="hd-actions">
      <a href="/" class="hd-btn" title="Voltar ao Pephub — Portal de Churn & Qualidade">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
        Portal Pephub
      </a>
      <a href="/churn/" class="hd-btn" title="Acessar o Painel de Churn Safra">Painel Safra</a>
      <a href="/fpd/" class="hd-btn" title="Acessar o Painel Executivo FPD">Painel FPD</a>
      <a href="/aprovacao-credito/" class="hd-btn" title="Acessar o Painel de Aprovação de Crédito">Crédito PF</a>
      <a href="/pep-tools/market-share/" class="hd-btn" title="Acessar o Market Share Studio">MS Studio</a>
      <div id="userWidget" style="display:flex;align-items:center;gap:8px"></div>
    </div>
  </div>
  <div class="hd-sub">
    <a href="/" class="back-hub" title="Voltar ao Pephub — Portal de Churn & Qualidade">‹ Portal Pephub</a>
    <span class="dot"></span>
    <span>Posição Oficial: <b>Julho / 2026 (Base Anatel)</b></span>
    <span class="dot"></span>
    <span>Regional Norte <b>(AM · AP · MA · PA · PI · RR)</b></span>
    <span class="dot"></span>
    <span>Escopo: <b>Móvel & Banda Larga Fixa</b></span>
    <div class="hd-right"><span>Planejamento & Performance · Regional Norte</span></div>
  </div>
</header>

<div class="wrap">

  <!-- Resumo de Indicadores Chave no Topo (CoverMeta) -->
  <div class="kpis" id="coverMeta" style="margin-bottom:14px;"></div>

  <!-- Painel de Navegação Executiva (Tabs Churn Safra) -->
  <div class="panel" style="margin-bottom:14px;">
    <h2>NAVEGAÇÃO EXECUTIVA <span class="note">Cortes analíticos, mapas e cruzamentos de convergência</span></h2>
    <div class="pbody" style="padding:10px 14px;">
      <nav class="tabs">
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

  <!-- Painel de Filtros Globais (Churn Safra Pattern com Gaveta) -->
  <div class="panel">
    <h2>
      FILTROS GLOBAIS <span class="note">Filtre por Estado, DDD, Município, Capital/Interior, Produto, Escopo e Pessoa</span>
      <button class="drawer-btn open" id="btnDrawer" onclick="toggleFilterDrawer()"><span id="drawerIco">▸</span> Filtros</button>
      <button class="hlp" data-h="filtros">?</button>
    </h2>
    <div class="pbody" id="fbody">
      <div class="filters-row">
        <span class="fl-lbl">Filtros:</span>
        <div class="ms" id="msUF"></div>
        <div class="ms" id="msDDD"></div>
        <div class="ms" id="msMun"></div>
        <div class="ms" id="msZona"></div>
        <div class="ms" id="msProd"></div>
        <div class="seg-pills" id="scopePills">
          <button data-v="ambos" class="on">Ambos</button><button data-v="movel">Móvel</button><button data-v="fixa">Fixa</button>
        </div>
        <div class="seg-pills" id="pessPills">
          <button data-v="todos" class="on">PF+PJ</button><button data-v="PF">PF</button><button data-v="PJ">PJ</button>
        </div>
      </div>
      <div class="tags" id="filterTags" style="margin-top:10px; border-top:1px solid var(--line2); padding-top:8px;"></div>
    </div>
  </div>

  <!-- Painel 1: Resumo Executivo -->
  <div class="panel" id="resumo">
    <h2>RESUMO EXECUTIVO <span class="note">Síntese executiva do mercado Móvel e Banda Larga na Regional Norte</span> <button class="hlp" data-h="resumo">?</button></h2>
    <div class="pbody">
      <p class="lead-txt">Dois mercados de dinâmica oposta: no <b>móvel</b> a Claro compete em toda a malha geográfica; na <b>Banda Larga fixa</b> os provedores regionais (ISPs) dominam de forma pulverizada e a Claro concentra sua força na <b>área cabeada</b> (14 cidades prioritárias). Utilize os filtros multidimensionais para recortar o panorama.</p>
      <div class="kpis" id="resumoCards"></div>
      <div class="chips" id="cityChips" style="display:none"></div>
    </div>
  </div>

  <!-- Painel 2: Mapa Geografico de Lideranca -->
  <div class="panel" id="mapa">
    <h2>MAPA GEOGRÁFICO DE LIDERANÇA <span class="note">Distribuição dos 454 municípios da Regional Norte pela cor da operadora líder</span> <button class="hlp" data-h="mapa">?</button></h2>
    <div class="pbody">
      <p class="lead-txt">Mapa vetorial cartográfico com os <b>454 municípios da Regional Norte coloridos pela liderança</b> de mercado. O anel dourado destaca as 14 cidades cabeadas Claro. Alterne entre móvel e fixa para visualizar a dominância espacial.</p>
      <div style="display:flex; align-items:center; gap:12px; margin-bottom:10px; flex-wrap:wrap;">
        <div class="toggle" id="mapToggle">
          <button data-m="mob" class="on">Líder Móvel</button>
          <button data-m="fix">Líder Banda Larga</button>
        </div>
        <div class="muted" id="mapCount" style="font-size:11.5px; font-weight:600;"></div>
      </div>
      <div class="maplegend" id="mapLegend"></div>
      <div class="mapbox" id="mapBox">
        <svg id="mapSvg" preserveAspectRatio="xMidYMid meet"></svg>
        <div id="mapTip" class="maptip"></div>
      </div>
      <p class="note">Choropleth municipal a partir da malha cartográfica vetorial. Municípios sem registros no recorte selecionado são exibidos em tom neutro.</p>
      
      <h3 style="font-size:12px; font-weight:700; text-transform:uppercase; letter-spacing:.5px; color:var(--ink2); margin:18px 0 6px;">Galeria de Players — Perfil e Posicionamento Estratégico</h3>
      <p class="lead-txt" style="margin-bottom:8px;">Clique em uma operadora para abrir o modal de desempenho analítico, municípios onde lidera e leitura de forças competitivas.</p>
      <div class="pgallery" id="playerGallery"></div>
    </div>
  </div>

  <!-- Painel 3: Movel por Produto -->
  <div class="panel" id="movel">
    <h2>
      MÓVEL — ABERTURA POR PRODUTO <span class="note">Acessos, share de mercado, saldo de adições líquidas e tempo estimado para liderança</span>
      <button class="btn-csv" onclick="exportTableToCSV('mobTable','panorama_movel.csv')">Exportar CSV</button>
      <button class="hlp" data-h="movel">?</button>
    </h2>
    <div class="pbody">
      <p class="lead-txt">Acompanhamento detalhado da concorrência no serviço móvel pessoal. Comparações diretas de base e share da Claro versus operadora líder, adições líquidas do último mês com média móvel trimestral, composição da carteira e gap analítico para alcançar a liderança.</p>
      <div class="sgt-wrap" id="mobTabs"></div>
      <div class="maplegend" id="mobLegend" style="margin-bottom:10px;"></div>
      <div class="kpis" id="mobKPIs"></div>
      <div class="tblwrap"><table id="mobTable"></table></div>
    </div>
  </div>

  <!-- Painel 4: Banda Larga Residencial -->
  <div class="panel" id="residencial">
    <h2>
      BANDA LARGA RESIDENCIAL <span class="note">Serviço 02.BL — Desempenho na área cabeada e no total regional</span>
      <button class="btn-csv" onclick="exportTableToCSV('resTable','panorama_banda_larga.csv')">Exportar CSV</button>
      <button class="hlp" data-h="residencial">?</button>
    </h2>
    <div class="pbody">
      <p class="lead-txt">Serviço de <b>Banda Larga Fixa (02.BL)</b>. Provedores regionais (ISPs) individualizados pelo nome real de mercado. O filtro padrão posiciona o foco sobre as <b>14 cidades cabeadas Claro (HFC/GPON)</b>, onde a infraestrutura proprietária viabiliza liderança competitiva.</p>
      <div style="margin-bottom:10px;">
        <div class="toggle" id="resToggle">
          <button data-s="cabled" class="on">Área Cabeada (14 Cidades)</button>
          <button data-s="total">Regional Norte Total</button>
        </div>
      </div>
      <div class="kpis" id="resKPIs"></div>
      <div class="tblwrap"><table id="resTable"></table></div>
    </div>
  </div>

  <!-- Painel 5: ISPs Individualizados -->
  <div class="panel" id="isp">
    <h2>
      ISPS — PROVEDORES REGIONAIS INDIVIDUALIZADOS <span class="note">Mapeamento de <span id="nispTotal"></span> provedores de banda larga na Regional Norte</span>
      <button class="btn-csv" onclick="exportTableToCSV('ispTable','panorama_isps.csv')">Exportar CSV</button>
      <button class="hlp" data-h="isp">?</button>
    </h2>
    <div class="pbody">
      <p class="lead-txt">Abertura dos provedores regionais de internet que compõem o mercado de banda larga fixa. Abaixo, destacam-se os maiores players locais por volume de acessos e capilaridade municipal.</p>
      <div class="grid g2" style="margin-bottom:14px;">
        <div class="card"><h3 style="margin:0 0 10px; font-size:12px; font-weight:700; text-transform:uppercase; color:var(--ink2);">Maiores ISPs (Acessos Banda Larga)</h3><div id="ispBars"></div></div>
        <div class="card"><h3 style="margin:0 0 10px; font-size:12px; font-weight:700; text-transform:uppercase; color:var(--ink2);">Top 3 ISPs em Destaque</h3><div id="top3isp"></div></div>
      </div>
      <h3 style="font-size:12px; font-weight:700; text-transform:uppercase; letter-spacing:.5px; color:var(--ink2); margin:18px 0 6px;">Desempenho Detalhado por Provedor</h3>
      <p class="lead-txt" style="margin-bottom:8px;">Base, fatia de mercado, adições líquidas mensais e trimestrais, variação MoM e índice de capilaridade municipal.</p>
      <div class="tblwrap"><table id="ispTable"></table></div>
    </div>
  </div>

  <!-- Painel 6: Comparador Claro × Concorrente -->
  <div class="panel" id="comparador">
    <h2>COMPARADOR — CLARO × CONCORRENTE <span class="note">Confronto direto e diferencial competitivo lado a lado</span> <button class="hlp" data-h="comparador">?</button></h2>
    <div class="pbody">
      <p class="lead-txt">Selecione o serviço (Móvel ou Fixa), o segmento e a operadora concorrente para comparar base instalada, share de mercado, adições líquidas e ritmo de crescimento no recorte geográfico filtrado.</p>
      <div class="selrow">
        <div class="toggle" id="cmpScope">
          <button data-s="movel" class="on">Móvel</button>
          <button data-s="fixa">Fixa</button>
        </div>
        <select id="cmpSeg"></select>
        <span class="muted" style="font-weight:700; font-size:12px;">VS</span>
        <select id="cmpB"></select>
      </div>
      <div id="cmpBody"></div>
    </div>
  </div>

  <!-- Painel 7: Cruzamentos Movel × Fixa -->
  <div class="panel" id="cruzamento">
    <h2>
      CRUZAMENTOS MÓVEL × RESIDENCIAL <span class="note">Dispersão e zonas de convergência de mercado por DDD</span>
      <button class="btn-csv" onclick="exportTableToCSV('quadTable','matriz_convergencia_ddd.csv')">Exportar CSV</button>
      <button class="hlp" data-h="scatter">?</button>
    </h2>
    <div class="pbody">
      <p class="lead-txt">Posicionamento de cada DDD da Regional Norte por penetração móvel Claro (Eixo X) versus participação na banda larga fixa (Eixo Y). O tamanho da bolha reflete o volume total de mercado e a cor identifica o líder móvel local.</p>
      <div id="scatter" style="margin-bottom:12px;"></div>
      <div class="maplegend" style="justify-content:center; margin-bottom:14px;">
        <span><i style="background:#E2231A"></i>Líder Móvel: Claro</span>
        <span><i style="background:#660099"></i>Líder Móvel: Vivo</span>
        <span><i style="background:#003399"></i>Líder Móvel: TIM</span>
      </div>
      <h3 style="font-size:12px; font-weight:700; text-transform:uppercase; letter-spacing:.5px; color:var(--ink2); margin:18px 0 6px;">Matriz de Convergência por DDD</h3>
      <div class="tblwrap"><table id="quadTable"></table></div>
    </div>
  </div>

  <!-- Painel 8: Oportunidades de Convergencia -->
  <div class="panel" id="oportunidades">
    <h2>
      OPORTUNIDADES DE CONVERGÊNCIA <span class="note">Mapeamento de praças para expansão de rede, mitigação de risco e conversão de base</span>
      <button class="btn-csv" onclick="exportTableToCSV('oppTable','oportunidades_convergencia.csv')">Exportar CSV</button>
      <button class="hlp" data-h="risco" title="Visão de Risco e Concentração de Mercado">?</button>
      <button class="hlp" data-h="oportunidades">?</button>
    </h2>
    <div class="pbody">
      <p class="lead-txt">Classificação estratégica das cidades da Regional Norte em três vetores de oportunidade: <b>Tipo A · Converter Fixa</b> (alta dominância móvel com banda larga fragmentada entre ISPs); <b>Tipo B · Crescer Móvel</b> (presença de rede fixa relevante com potencial para cross-sell móvel); <b>Tipo C · Desenvolvimento</b> (mercados em rápida expansão com presença de concorrentes e demanda latente por conectividade). Clique em <b>Simulador</b> ou <b>detalhes</b> para abrir o perfil sociodemográfico (IBGE/Anatel).</p>
      <div class="sgt-wrap" id="oppPills"></div>
      <div class="tblwrap"><table id="oppTable"></table></div>
      
      <h3 style="font-size:12px; font-weight:700; text-transform:uppercase; letter-spacing:.5px; color:var(--ink2); margin:20px 0 8px;">Recomendações Estratégicas por Vetor</h3>
      <div class="ins" style="border-left-color: var(--green);">
        <h4>Tipo A · Ativação de Combo nas Cidades Cabeadas</h4>
        <p>Onde a Claro já dispõe de rede cabeada ativa e lidera o segmento móvel, acelerar a oferta convergente sobre a base instalada a baixo custo de aquisição (CAC).</p>
      </div>
      <div class="ins" style="border-left-color: var(--amber);">
        <h4>Tipo B · Cross-Sell Móvel sobre Assinantes Fixos</h4>
        <p>Praças onde a banda larga fixa Claro possui base representativa porém o share móvel é inferior à média, intensificar campanhas de portabilidade e ofertas combo multiplay.</p>
      </div>
      <div class="ins" style="border-left-color: var(--red);">
        <h4>Tipo C · Entrada Antecipada em Polos de Desenvolvimento (Gestão de Risco)</h4>
        <p>Municípios com forte dinamismo econômico (mineração e agronegócio em PA e MA) dominados por uma única operadora concorrente: planejar antecipação de cobertura FTTH/FWA e prospecção corporativa B2B, reduzindo o risco de consolidação adversa.</p>
      </div>
    </div>
  </div>

  <!-- Painel 9: Metodologia -->
  <div class="panel" id="metodo">
    <h2>NOTAS METODOLÓGICAS & CRITÉRIOS ANATEL <span class="note">Fontes de dados oficiais, periodicidade e calibração estatística</span> <button class="hlp" data-h="metodo">?</button></h2>
    <div class="pbody">
      <div class="grid g2" style="margin-bottom:14px;">
        <div class="card">
          <h3 style="margin:0 0 6px; font-size:12px; font-weight:700; text-transform:uppercase; color:var(--ink2);">Segmento Móvel Pessoal (SMP)</h3>
          <p style="font-size:12.5px; color:var(--ink2); line-height:1.6;">Base calibrada a partir do painel oficial Anatel para a Regional Norte por DDD, segmento e operadora. Detalhamento municipal apurado via Base Município Anatel. Adições líquidas do mês correspondem à variação jul/26 vs jun/26; média trimestral calculada pelo intervalo jul/26 a abr/26 dividido por 3.</p>
        </div>
        <div class="card">
          <h3 style="margin:0 0 6px; font-size:12px; font-weight:700; text-transform:uppercase; color:var(--ink2);">Serviço de Comunicação Multimídia (SCM)</h3>
          <p style="font-size:12.5px; color:var(--ink2); line-height:1.6;">Acessos de Banda Larga Fixa (02.BL) com provedores regionais individualizados via coluna ABERTURA. A delimitação de 14 cidades cabeadas reflete as praças com presença de rede HFC e GPON da Claro. Indicadores de liderança, posições e gaps utilizam o ranking por CNPJ de outorga.</p>
        </div>
      </div>
      <div class="card" style="margin-bottom:14px;">
        <h3 style="margin:0 0 6px; font-size:12px; font-weight:700; text-transform:uppercase; color:var(--ink2);">Motor de Simulação & Projeção Linear</h3>
        <p style="font-size:12.5px; color:var(--ink2); line-height:1.6;">Todas as visões recalculam em tempo real a partir dos fatos por Município × Produto × Natureza Jurídica × Operadora. O cálculo de tempo estimado para alcançar a liderança projeta cada competidor à sua taxa média trimestral recente e a Claro com o multiplicador de incremento parametrizado no controle deslizante.</p>
      </div>
      <div class="card" style="margin-bottom:14px;">
        <h3 style="margin:0 0 6px; font-size:12px; font-weight:700; text-transform:uppercase; color:var(--ink2);">Fontes Estatísticas & Dados Sociodemográficos</h3>
        <ul style="font-size:12px; color:var(--ink2); line-height:1.8; padding-left:18px; margin:6px 0;">
          <li><b>IBGE — Censo Demográfico 2022:</b> População residente, domicílios particulares e densidade demográfica.</li>
          <li><b>IBGE — Produto Interno Bruto dos Municípios:</b> PIB total a preços correntes e PIB per capita municipal.</li>
          <li><b>PNUD / IPEA / FJP:</b> Índice de Desenvolvimento Humano Municipal (IDHM).</li>
          <li><b>MTE / Novo CAGED:</b> Remuneração média do trabalho formal para as praças-âncora da Regional Norte.</li>
          <li><b>SIMET / NIC.br & Anatel (RQUAL):</b> Indicadores de qualidade de rede fixa (IQC), velocidade medida e selo de qualidade municipal.</li>
          <li><b>Radar da Telecom / CNO (Receita Federal):</b> Obras ativas e expansão predial como proxy de demanda residencial FTTH.</li>
        </ul>
      </div>
    </div>
  </div>

  <div id="modalRoot" style="display:none"></div>

  <footer>
    <b>Panorama de Market Share — Móvel & Banda Larga Residencial · Regional Norte</b><br>
    Posição Oficial: Julho / 2026 · Elaborado pela equipe de Planejamento & Performance RNO.<br>
    Documento analítico executivo para uso corporativo exclusivo Claro Brasil.
  </footer>

</div> <!-- fim .wrap -->
"""

help_script = """
const HELP = {
  filtros: "Filtros multidimensionais que restringem a base por UF, DDD, Município, Capital/Interior, Produto, Escopo geográfico e Pessoa (PF/PJ).",
  resumo: "Síntese executiva do volume total de acessos, fatias de mercado e posição da Claro versus concorrentes na Regional Norte.",
  mapa: "Distribuição espacial dos 454 municípios da Regional Norte identificando a operadora líder em cada mercado local.",
  movel: "Abertura analítica do segmento móvel entre pré-pago, pós-pago, M2M e tecnologias celulares com gaps para a liderança.",
  residencial: "Desempenho da banda larga fixa residencial (02.BL) na área cabeada oficial e no total regional.",
  isp: "Ranking e perfil dos provedores regionais de internet (ISPs) individualizados com capilaridade municipal.",
  comparador: "Confronto direto lado a lado e cálculo do diferencial competitivo entre a Claro e a operadora selecionada.",
  scatter: "Matriz de dispersão e correlação entre penetração móvel e participação na banda larga fixa por DDD.",
  oportunidades: "Mapeamento estratégico de praças para expansão de infraestrutura FTTH/FWA e conversão de base convergente.",
  metodo: "Notas metodológicas, fontes estatísticas oficiais (Anatel, IBGE, SIMET) e critérios de calibração.",
  risco: "Visão de Risco & Concentração: Análise de exposição de mercado, pressão competitiva de provedores regionais e risco de perda de share."
};

document.addEventListener('click', function(e) {
  if (e.target && e.target.classList && e.target.classList.contains('hlp')) {
    const key = e.target.getAttribute('data-h');
    if (HELP[key]) alert(HELP[key]);
  }
});

// Gaveta de Filtros Retratil
function toggleFilterDrawer() {
  const fb = document.getElementById('fbody');
  const btn = document.getElementById('btnDrawer');
  if (!fb) return;
  if (fb.style.display === 'none') {
    fb.style.display = 'block';
    if (btn) btn.classList.add('open');
  } else {
    fb.style.display = 'none';
    if (btn) btn.classList.remove('open');
  }
}

// Exportacao CSV no Cliente (Blob / createObjectURL)
function exportTableToCSV(tableId, filename) {
  const table = document.getElementById(tableId);
  if (!table) return;
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
  a.download = filename || 'panorama_market_share.csv';
  a.click();
}

// Navegacao com Abas (.tabs a.on)
document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('.tabs a').forEach(a => {
    a.addEventListener('click', function(e) {
      document.querySelectorAll('.tabs a').forEach(el => el.classList.remove('on'));
      this.classList.add('on');
    });
  });
});

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
          <button id="btnLogoutPanorama" style="background:none;border:1px solid rgba(255,255,255,.3);color:#fff;padding:4px 8px;border-radius:3px;font-size:10.5px;cursor:pointer;font-weight:600">Sair</button>
        `;
        const btnLogout = document.getElementById('btnLogoutPanorama');
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
<title>Panorama Market Share — Móvel & Residencial · Regional Norte</title>
<style>{css_content}</style>
</head>
<body>
{html_body}
<script>{data_script}</script>
<script>{engine_script}</script>
<script>{help_script}</script>
</body>
</html>
"""

with open('public_staging/panorama-market-share/index.html', 'w', encoding='utf-8') as f:
    f.write(full_html)

print("Recreated public_staging/panorama-market-share/index.html successfully from pristine source!")
