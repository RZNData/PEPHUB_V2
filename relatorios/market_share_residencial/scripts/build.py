"""
Build Script para o Relatório Oficial de Market Share Residencial (Regional Norte)
Conformidade rigorosa com PADRAO_DESIGN_PAINEIS.md e modelo Churn Safra:
  1. Visão Resumida: 4 quadros (Market Share, Net Adds, Base, Net Share) comparando os principais players e Outros,
     com sinalização do melhor da linha, coluna de posição da Claro e seletor de dimensão (DDD, UF, Regional).
  2. Visão Detalhada: Matriz histórica mensal (14 meses) com 4 linhas por player (Base, Share %, Net Adds, Net Share %),
     abertura de DDDs colapsável e retorno do bloco completo de Projeção de Ultrapassagem do Líder.
  3. Visão por Município: Corrigida e 100% funcional com cidades polo normalizadas e subtotais.
  4. Pré-set padrão inicial: Banda Larga Fixa (02.BL) + GPON+HFC (Fibra + Cable Modem).
  5. Gaveta de filtros retrátil com multi-seleção, busca e ordenação dependente (.na no final).
"""

import os
import sys
import json
import time
import openpyxl

try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
REP_DIR = os.path.join(ROOT_DIR, "relatorios", "market_share_residencial")
EXCEL_PATH = os.path.join(REP_DIR, "dados", "Agosto_2026_Mkt_Share_Residencial_v9.2.xlsm")
OUTPUT_HTML = os.path.join(REP_DIR, "index.html")

def build():
    print("Compilando Market Share Residencial Oficial (4 Quadros + Detalhada Histórica + Projeção)...")
    if not os.path.exists(EXCEL_PATH):
        print(f"❌ Erro: Planilha não encontrada em {EXCEL_PATH}")
        return False

    t0 = time.time()
    wb = openpyxl.load_workbook(EXCEL_PATH, read_only=True, data_only=True)

    # 1. Meses Analíticos (14 meses: jul/25 a ago/26)
    months = ['jul/25', 'ago/25', 'set/25', 'out/25', 'nov/25', 'dez/25', 'jan/26', 'fev/26', 'mar/26', 'abr/26', 'mai/26', 'jun/26', 'jul/26', 'ago/26']

    # 2. Extração da Base Analítica Completa
    print("  • Extraindo Base_Analitica e dicionários de dimensões...")
    ws_an = wb['Base_Analitica']

    dim_keys = ['cidade', 'grupo', 'empresa', 'ddd', 'uf', 'servico', 'tipo_cidade', 'tipo_cliente', 'velocidade', 'tecnologia', 'tipo_mercado']
    dicts = {k: [] for k in dim_keys}
    d_maps = {k: {} for k in dim_keys}

    def get_id(dim, val):
        v = str(val or '').strip()
        if not v:
            v = 'N/I'
        if v not in d_maps[dim]:
            idx = len(dicts[dim])
            dicts[dim].append(v)
            d_maps[dim][v] = idx
            return idx
        return d_maps[dim][v]

    records = []
    for r, row in enumerate(ws_an.iter_rows(values_only=True)):
        if r == 0:
            continue
        # Meses de col 91 (202507) a col 104 (202608)
        m14 = [int(row[c] or 0) for c in range(91, 105)]
        if not any(m14):
            continue

        cidade_id = get_id('cidade', row[5] or row[0])
        grupo_id = get_id('grupo', row[1])
        empresa_id = get_id('empresa', row[2])
        ddd_id = get_id('ddd', str(row[3]))
        uf_id = get_id('uf', row[4])
        servico_id = get_id('servico', row[6])
        tipo_cidade_id = get_id('tipo_cidade', row[8])
        tipo_cliente_id = get_id('tipo_cliente', row[10])
        velocidade_id = get_id('velocidade', row[11])
        tecnologia_id = get_id('tecnologia', row[12])
        tipo_mercado_id = get_id('tipo_mercado', row[105])

        records.append([
            cidade_id, grupo_id, empresa_id, ddd_id, uf_id,
            servico_id, tipo_cidade_id, tipo_cliente_id, velocidade_id, tecnologia_id, tipo_mercado_id,
            m14
        ])

    print(f"  • Registros carregados: {len(records)} em {time.time()-t0:.2f}s")

    # 3. Lista oficial de Municípios Polo (com código exato em D.cidade e UF)
    polo_cities = [
        {'code': 'BELEM', 'name': 'Belém (PA)', 'uf': 'PA', 'ddd': '91'},
        {'code': 'MANAUS', 'name': 'Manaus (AM)', 'uf': 'AM', 'ddd': '92'},
        {'code': 'SAO LUIS', 'name': 'São Luís (MA)', 'uf': 'MA', 'ddd': '98'},
        {'code': 'MACAPA', 'name': 'Macapá (AP)', 'uf': 'AP', 'ddd': '96'},
        {'code': 'BOA VISTA', 'name': 'Boa Vista (RR)', 'uf': 'RR', 'ddd': '95'},
        {'code': 'ANANINDEUA', 'name': 'Ananindeua (PA)', 'uf': 'PA', 'ddd': '91'},
        {'code': 'SANTAREM', 'name': 'Santarém (PA)', 'uf': 'PA', 'ddd': '93'},
        {'code': 'MARABA', 'name': 'Marabá (PA)', 'uf': 'PA', 'ddd': '94'},
        {'code': 'IMPERATRIZ', 'name': 'Imperatriz (MA)', 'uf': 'MA', 'ddd': '99'},
        {'code': 'CASTANHAL', 'name': 'Castanhal (PA)', 'uf': 'PA', 'ddd': '91'},
        {'code': 'PARAUAPEBAS', 'name': 'Parauapebas (PA)', 'uf': 'PA', 'ddd': '94'},
        {'code': 'ABAETETUBA', 'name': 'Abaetetuba (PA)', 'uf': 'PA', 'ddd': '91'},
        {'code': 'CAMETA', 'name': 'Cametá (PA)', 'uf': 'PA', 'ddd': '91'},
        {'code': 'BRAGANCA', 'name': 'Bragança (PA)', 'uf': 'PA', 'ddd': '91'},
        {'code': 'BARCARENA', 'name': 'Barcarena (PA)', 'uf': 'PA', 'ddd': '91'},
        {'code': 'ALTAMIRA', 'name': 'Altamira (PA)', 'uf': 'PA', 'ddd': '93'},
        {'code': 'TUCURUI', 'name': 'Tucuruí (PA)', 'uf': 'PA', 'ddd': '94'},
        {'code': 'PARAGOMINAS', 'name': 'Paragominas (PA)', 'uf': 'PA', 'ddd': '91'},
        {'code': 'ITAITUBA', 'name': 'Itaituba (PA)', 'uf': 'PA', 'ddd': '93'},
        {'code': 'CAPANEMA', 'name': 'Capanema (PA)', 'uf': 'PA', 'ddd': '91'}
    ]

    payload = {
        'mes_referencia': 'Agosto/2026',
        'data_posicao': '21/09/2026',
        'months': months,
        'dicts': dicts,
        'rows': records,
        'polo_cities': polo_cities
    }

    print("  • Gerando HTML com Design System e Motor Dinâmico...")
    html_content = generate_html(payload)
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)

    size_kb = os.path.getsize(OUTPUT_HTML) / 1024
    print(f"✅ Painel gerado com sucesso em: {OUTPUT_HTML} ({size_kb:.1f} KB)")
    return True


def generate_html(payload):
    json_data = json.dumps(payload, separators=(',', ':'), ensure_ascii=False)

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Market Share Residencial — Regional Norte</title>

<!-- PWA & Mobile Web App Meta Tags -->
<link rel="manifest" href="/manifest.webmanifest">
<meta name="theme-color" content="#8a0f18">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="PEP HUB">
<link rel="apple-touch-icon" href="/icons/apple-touch-icon.png">
<link rel="icon" type="image/svg+xml" href="/icons/icon.svg">
<link rel="icon" type="image/png" sizes="32x32" href="/icons/favicon.png">
<link rel="stylesheet" href="/css/app-mobile.css">

<style>
:root {{
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
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  background: var(--bg);
  color: var(--ink);
  font: 13px/1.45 "Segoe UI", Roboto, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
}}
header {{ background: #ffffff; }}
.hd-bar {{
  background: linear-gradient(90deg, #8a0f18 0%, #c0191f 26%, #e23a1e 50%, #f47a1f 74%, #f9b233 100%);
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 14px 26px;
}}
.hd-ico {{
  width: 46px;
  height: 46px;
  min-width: 46px;
  border-radius: 50%;
  border: 2.4px solid rgba(255,255,255,.95);
  display: flex;
  align-items: center;
  justify-content: center;
}}
.hd-bar h1 {{
  margin: 0;
  color: #ffffff;
  font-size: 30px;
  font-weight: 400;
  letter-spacing: -.4px;
  line-height: 1.05;
  display: flex;
  align-items: baseline;
  gap: 11px;
  flex-wrap: wrap;
}}
.hd-bar h1 b {{ font-weight: 800; letter-spacing: -1px; text-transform: none; }}
.hd-bar h1 span {{ font-weight: 300; font-size: 24px; color: rgba(255,255,255,.93); }}
.hd-sub {{
  background: var(--nav);
  color: #aab4c0;
  font-size: 11.5px;
  padding: 7px 26px;
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}}
.hd-sub b {{ color: #e8edf3; font-weight: 600; }}
.hd-sub .dot {{ width: 3px; height: 3px; border-radius: 50%; background: #5b6675; display: inline-block; }}
.hd-sub .hd-right {{ margin-left: auto; display: flex; align-items: center; gap: 12px; }}
.back-hub {{
  color: #f9b233;
  text-decoration: none;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  transition: color .15s;
}}
.back-hub:hover {{ color: #ffffff; text-decoration: underline; }}

@media(max-width: 820px) {{
  .hd-bar h1 {{ font-size: 22px; }}
  .hd-bar h1 span {{ font-size: 17px; }}
}}

.wrap {{ padding: 16px 26px 40px; max-width: 2400px; margin: 0 auto; }}
.panel {{ background: var(--panel); border: 1px solid var(--line); border-radius: 3px; margin-bottom: 14px; }}
.panel > h2 {{
  margin: 0;
  padding: 10px 14px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: .6px;
  color: var(--ink2);
  border-bottom: 1px solid var(--line2);
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}}
.panel > h2 .note {{ text-transform: none; letter-spacing: 0; font-weight: 400; color: var(--ink3); font-size: 11px; }}
.pbody {{ padding: 14px; }}

/* Helper '?' */
.hlp {{
  margin-left: auto;
  width: 19px;
  height: 19px;
  min-width: 19px;
  border-radius: 50%;
  border: 1px solid var(--line);
  background: #ffffff;
  color: var(--ink3);
  font: 600 11px "Segoe UI", Arial;
  line-height: 1;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  flex: none;
}}
.hlp:hover {{ background: var(--nav); color: #ffffff; border-color: var(--nav); }}

/* ---- Filtros Gaveta Retrátil (Padrão Churn Safra) ---- */
.drawer-btn {{
  display: inline-flex;
  align-items: center;
  gap: 7px;
  background: var(--nav);
  color: #ffffff;
  border: 1px solid var(--nav);
  font-size: 11.5px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: .5px;
  padding: 5px 13px;
  border-radius: 2px;
  cursor: pointer;
}}
.drawer-btn:hover {{ background: var(--nav2); }}
.drawer-btn span {{ font-size: 10px; transition: transform .15s; }}
.drawer-btn.open span {{ transform: rotate(90deg); }}

.filters {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(196px, 1fr));
  gap: 11px;
}}
.f {{
  border: 1px solid var(--line2);
  border-radius: 3px;
  padding: 7px 8px 8px;
  background: #fcfcfd;
}}
.f > label {{
  display: flex;
  align-items: center;
  font-size: 10.5px;
  text-transform: uppercase;
  letter-spacing: .5px;
  color: var(--ink3);
  margin-bottom: 4px;
}}
.f .cnt {{ margin-left: auto; text-transform: none; letter-spacing: 0; color: #b3bac3; font-size: 10px; }}
.frow {{ display: flex; gap: 4px; margin-bottom: 4px; }}
.frow input {{
  flex: 1;
  min-width: 0;
  border: 1px solid var(--line);
  border-radius: 2px;
  padding: 3px 6px;
  font: 11.5px "Segoe UI", Arial;
  color: var(--ink);
}}
.frow input:focus {{ outline: none; border-color: var(--blue); }}
.fbtn {{
  border: 1px solid var(--line);
  background: #ffffff;
  border-radius: 2px;
  padding: 0 6px;
  font-size: 11px;
  line-height: 1;
  color: var(--ink2);
  cursor: pointer;
  flex: none;
}}
.fbtn:hover {{ background: #eef1f4; color: var(--ink); }}
.fbtn.act {{ background: var(--nav); color: #ffffff; border-color: var(--nav); }}
.f select[multiple] {{
  width: 100%;
  height: 96px;
  border: 1px solid var(--line);
  background: #ffffff;
  border-radius: 2px;
  padding: 2px;
  font: 12px "Segoe UI", Arial;
  color: var(--ink);
}}
.f select:focus {{ outline: none; border-color: var(--blue); }}
.f .sel {{ font-size: 10px; color: var(--blue); margin-top: 3px; min-height: 12px; }}
.f select[multiple] option.na {{ color: #c3c9d1; font-style: italic; }}
.f .na-note {{ font-size: 9.5px; color: #b3bac3; margin-top: 2px; }}

.fbar {{
  display: flex;
  gap: 8px;
  align-items: center;
  margin-top: 12px;
  flex-wrap: wrap;
  border-top: 1px solid var(--line2);
  padding-top: 10px;
}}
button {{
  border: 1px solid var(--line);
  background: #ffffff;
  color: var(--ink);
  padding: 5px 12px;
  border-radius: 2px;
  cursor: pointer;
  font: 12px "Segoe UI", Arial;
}}
button:hover {{ background: #f0f2f5; }}
button.primary {{ background: var(--nav); color: #ffffff; border-color: var(--nav); }}
button.primary:hover {{ background: var(--nav2); }}
.chips {{ display: flex; gap: 6px; flex-wrap: wrap; margin-left: auto; }}
.chip {{
  background: #eef1f4;
  border: 1px solid var(--line);
  border-radius: 2px;
  padding: 2px 8px;
  font-size: 11px;
  color: var(--ink2);
}}

/* Quick DDD Pills */
.ddd-pills {{ display: flex; gap: 4px; flex-wrap: wrap; }}
.ddd-pill {{
  border: 1px solid var(--line);
  background: #ffffff;
  padding: 4px 10px;
  font-size: 11.5px;
  font-weight: 600;
  border-radius: 2px;
  cursor: pointer;
  color: var(--ink2);
}}
.ddd-pill:hover {{ background: #f0f2f5; }}
.ddd-pill.act {{ background: var(--red); color: #ffffff; border-color: var(--red); }}

/* View Tabs & Sub-Tabs */
.view-tabs, .tabs {{ display: flex; gap: 4px; }}
.tab-btn, .tab-dim-btn {{
  border: 1px solid var(--line);
  background: #ffffff;
  padding: 5px 14px;
  font-size: 11.5px;
  font-weight: 600;
  border-radius: 2px;
  cursor: pointer;
  color: var(--ink2);
}}
.tab-btn:hover, .tab-dim-btn:hover {{ background: #f0f2f5; }}
.tab-btn.on, .tab-dim-btn.on {{ background: var(--nav); color: #ffffff; border-color: var(--nav); }}

/* KPIs */
.kpis {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  border-top: 1px solid var(--line2);
}}
.kpi {{
  padding: 12px 14px;
  border-right: 1px solid var(--line2);
  border-bottom: 1px solid var(--line2);
}}
.kpi .k {{ font-size: 10.5px; text-transform: uppercase; letter-spacing: .5px; color: var(--ink3); }}
.kpi .v {{ font-size: 22px; font-weight: 600; margin-top: 3px; letter-spacing: -.3px; }}
.kpi .d {{ font-size: 11px; color: var(--ink2); margin-top: 2px; }}
.kpi.acc .v {{ color: var(--red); }}
.kpi.green .v {{ color: var(--green); }}

/* Tables */
table {{ width: 100%; border-collapse: collapse; font-size: 12px; }}
th, td {{ padding: 6px 8px; border-bottom: 1px solid var(--line2); text-align: right; white-space: nowrap; }}
th {{
  background: #f7f8fa;
  color: var(--ink2);
  font-weight: 600;
  font-size: 10.5px;
  text-transform: uppercase;
  letter-spacing: .3px;
  position: sticky;
  top: 0;
  z-index: 2;
}}
th.l, td.l {{ text-align: left; }}
tbody tr:hover {{ background: #f7f9fb; }}
tfoot td {{ font-weight: 600; background: #f7f8fa; border-top: 2px solid var(--line); }}
.scroll {{ max-height: 520px; overflow: auto; border: 1px solid var(--line2); }}

/* Quadrant Layout for ISPs & Resumo */
.quad-grid {{
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}}
@media(max-width: 1200px) {{
  .quad-grid {{ grid-template-columns: 1fr; }}
}}
.quad-card {{
  background: #ffffff;
  border: 1px solid var(--line);
  border-radius: 3px;
}}
.quad-card h3 {{
  margin: 0;
  padding: 9px 12px;
  font-size: 11.5px;
  text-transform: uppercase;
  letter-spacing: .5px;
  font-weight: 700;
  color: var(--ink2);
  border-bottom: 1px solid var(--line2);
  background: #fafbfc;
  display: flex;
  justify-content: space-between;
}}
.quad-card h3 span.sub {{
  font-size: 10px;
  font-weight: 400;
  color: var(--ink3);
  text-transform: none;
}}

/* Badges e Destaques */
.best-val {{
  background: #eaf6ec !important;
  color: #1e6b37 !important;
  font-weight: 700 !important;
}}
.pos-badge {{
  display: inline-block;
  padding: 1px 7px;
  border-radius: 9px;
  font-size: 10px;
  font-weight: 700;
}}
.pos-1 {{ background: #eaf6ec; color: #1e6b37; border: 1px solid #b8e2c4; }}
.pos-2 {{ background: #fff8e6; color: #a16207; border: 1px solid #fde047; }}
.pos-3 {{ background: #f1f5f9; color: #475569; border: 1px solid #cbd5e1; }}
.pos-other {{ background: #f8fafc; color: #94a3b8; border: 1px solid #e2e8f0; }}

.pos {{ color: var(--green); font-weight: 600; }}
.neg {{ color: var(--red); font-weight: 600; }}
.neu {{ color: var(--ink3); }}
.claro-row td {{ font-weight: 700; background: #fff8f8; border-left: 3px solid #c0392b; }}
.vivo-row td {{ font-weight: 700; background: #faf6fd; border-left: 3px solid #6b4b8a; }}
.tim-row td {{ font-weight: 700; background: #f4f8fc; border-left: 3px solid #2a5d8f; }}
.oi-row td {{ font-weight: 700; background: #fffdf5; border-left: 3px solid #c98a15; }}
.sky-row td {{ font-weight: 700; background: #fff9f5; border-left: 3px solid #e67e22; }}
.outros-row td {{ font-weight: 700; background: #f9fafb; border-left: 3px solid #7f8c8d; }}
.isp-tot-row td {{ font-weight: 700; background: #f8fafc; border-bottom: 2px solid var(--line); border-left: 3px solid var(--nav); }}
.total-row td {{ font-weight: 700; background: #f1f5f9; border-top: 2px solid var(--line); }}

.col-cur-mth {{ background: rgba(224, 32, 32, 0.04) !important; font-weight: 700 !important; }}
th.col-cur-mth-hdr {{ background: #fdf2f2 !important; color: var(--red) !important; border-bottom: 2px solid var(--red) !important; }}

/* Line Chart & Visuals */
.chart-box {{
  padding: 16px 18px;
  background: #ffffff;
  border-bottom: 1px solid var(--line2);
}}
.chart-legend {{
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  align-items: center;
  margin-bottom: 12px;
}}
.chart-leg-item {{
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11.5px;
  font-weight: 600;
  color: var(--ink);
}}
.chart-leg-dot {{
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
}}
.chart-svg-wrap {{
  width: 100%;
  overflow-x: auto;
}}
.btn-toggle-ddd {{
  padding: 4px 10px;
  font-size: 11px;
  font-weight: 600;
  border: 1px solid var(--line);
  background: #ffffff;
  border-radius: 2px;
  cursor: pointer;
  color: var(--ink2);
}}
.btn-toggle-ddd:hover {{ background: #f0f2f5; }}

/* Card Projeção de Ultrapassagem */
.proj-box {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
  padding: 12px;
}}
.proj-card {{
  border: 1px solid var(--line);
  border-radius: 3px;
  padding: 10px 12px;
  background: #fcfcfd;
}}
.proj-card .lbl {{ font-size: 10.5px; text-transform: uppercase; color: var(--ink3); font-weight: 600; letter-spacing: .4px; }}
.proj-card .val {{ font-size: 19px; font-weight: 700; color: var(--ink); margin-top: 3px; }}
.proj-card .desc {{ font-size: 11px; color: var(--ink2); margin-top: 2px; }}

/* Modal */
.modal {{
  position: fixed;
  inset: 0;
  background: rgba(18,24,32,.55);
  display: none;
  z-index: 99;
  align-items: center;
  justify-content: center;
  padding: 24px;
}}
.modal.on {{ display: flex; }}
.modal .box {{
  background: #ffffff;
  max-width: 720px;
  width: 100%;
  max-height: 82vh;
  overflow: auto;
  border-radius: 4px;
  box-shadow: 0 14px 48px rgba(0,0,0,.3);
}}
.modal .hd {{
  padding: 14px 18px;
  border-bottom: 1px solid var(--line2);
  display: flex;
  align-items: center;
  position: sticky;
  top: 0;
  background: #ffffff;
}}
.modal .hd h3 {{ margin: 0; font-size: 14px; font-weight: 600; }}
.modal .hd button {{
  margin-left: auto;
  border: none;
  background: none;
  font-size: 20px;
  line-height: 1;
  color: var(--ink3);
  cursor: pointer;
}}
.modal .bd {{ padding: 16px 18px; font-size: 12.5px; line-height: 1.7; color: var(--ink2); }}
</style>
</head>
<body>

<header>
  <div class="hd-bar">
    <div class="hd-ico">
      <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2">
        <circle cx="12" cy="12" r="10"/>
        <polygon points="12 2 15 10 12 8 9 10" fill="#ffffff" stroke="none"/>
        <polygon points="12 22 15 14 12 16 9 14" fill="rgba(255,255,255,0.4)" stroke="none"/>
        <polygon points="2 12 10 9 8 12 10 15" fill="rgba(255,255,255,0.4)" stroke="none"/>
        <polygon points="22 12 14 9 16 12 14 15" fill="#ffffff" stroke="none"/>
      </svg>
    </div>
    <h1>
      <b>Market Share Residencial</b>
      <span>Regional Norte</span>
    </h1>
    <div id="mktUserWidget" style="margin-left:auto;display:flex;align-items:center;gap:8px"></div>
  </div>
  <div class="hd-sub">
    <a href="/" class="back-hub" title="Voltar ao Portal Pephub">‹ Portal Pephub</a>
    <span class="dot"></span>
    <span><b>{payload['mes_referencia']}</b> · Posição Oficial Anatel</span>
    <span class="dot"></span>
    <span>Base Consolidada <b>Banda Larga Fixa (GPON + HFC)</b></span>
    <span class="dot"></span>
    <span>Regional Norte (PA, AM, AP, MA, RR)</span>
    <span class="hd-right">
      <span>Posição <b>{payload['data_posicao']}</b> · <b id="hdrRows">{len(payload['rows']):,} registros</b></span>
    </span>
  </div>
</header>

<div class="wrap">

  <!-- PAINEL GAVETA DE FILTROS RETRÁTIL -->
  <div class="panel" id="pnFiltros">
    <h2 style="cursor:pointer" id="fToggleBar">
      <button class="drawer-btn" id="btnDrawer"><span id="drawerIco">▸</span> Filtros</button>
      <span class="note" id="fSummary">padrão ativo: Banda Larga (02.BL) · GPON + HFC (Fibra + Cable Modem)</span>
      <button class="hlp" data-h="filtros">?</button>
    </h2>
    <div class="pbody" id="fDrawer" style="display:none">
      <div class="filters" id="filters"></div>
      <div class="fbar">
        <button class="primary" id="btnApply">Aplicar Filtros</button>
        <button id="btnClear">Resetar para Padrão (GPON+HFC)</button>
        <button id="btnClearAll">Limpar Todos os Filtros</button>
        <button id="btnCsv">Exportar visão (CSV)</button>
        <div class="chips" id="chips"></div>
      </div>
    </div>
  </div>

  <!-- BARRA DE CONTROLE: FILTRO RÁPIDO DDD + ABAS DE VISÃO -->
  <div class="panel" style="margin-bottom:14px;padding:8px 14px;background:#fff;display:flex;align-items:center;gap:14px;flex-wrap:wrap">
    <div style="display:flex;align-items:center;gap:8px">
      <span style="font-size:11px;font-weight:700;color:var(--ink2);text-transform:uppercase;letter-spacing:.5px">Filtrar DDD:</span>
      <div class="ddd-pills" id="dddPills">
        <button class="ddd-pill act" data-ddd="TODOS">TODOS</button>
        <button class="ddd-pill" data-ddd="91">91</button>
        <button class="ddd-pill" data-ddd="92">92</button>
        <button class="ddd-pill" data-ddd="93">93</button>
        <button class="ddd-pill" data-ddd="94">94</button>
        <button class="ddd-pill" data-ddd="95">95</button>
        <button class="ddd-pill" data-ddd="96">96</button>
        <button class="ddd-pill" data-ddd="97">97</button>
        <button class="ddd-pill" data-ddd="98">98</button>
        <button class="ddd-pill" data-ddd="99">99</button>
      </div>
    </div>
    <div class="view-tabs" id="viewTabs" style="margin-left:auto">
      <button class="tab-btn on" data-tab="resumida">Visão Resumida</button>
      <button class="tab-btn" data-tab="isp">Visão ISP's</button>
      <button class="tab-btn" data-tab="municipio">Por Município</button>
      <button class="tab-btn" data-tab="detalhada">Visão Detalhada</button>
    </div>
  </div>

  <!-- INDICADORES (KPIS) -->
  <div class="panel">
    <h2>Indicadores Oficiais — Claro Residencial <span class="note" id="kpiScopeNote">Regional Norte · Banda Larga Fixa (GPON + HFC)</span><button class="hlp" data-h="kpis">?</button></h2>
    <div class="kpis" id="kpis"></div>
  </div>

  <!-- VISÃO 1: RESUMIDA (4 QUADROS COMPARATIVOS + SELETOR REGIONAL / UF / DDD) -->
  <div id="viewResumida" class="tab-content">
    <div class="panel" style="margin-bottom:14px">
      <h2>
        Visão Resumida — Comparativo dos Principais Players & Outros
        <span class="note">4 dimensões analíticas simultâneas com destaque do líder e posição da Claro</span>
        <button class="hlp" data-h="resumida">?</button>
      </h2>
      <div class="pbody" style="padding-bottom:6px">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;flex-wrap:wrap;gap:10px">
          <div style="font-size:11.5px;font-weight:700;color:var(--ink2);text-transform:uppercase;letter-spacing:.5px">
            Dimensão de Abertura:
          </div>
          <div class="tabs" id="tabsResumoDim">
            <button class="tab-dim-btn on" data-dim="ddd">Abertura por DDD</button>
            <button class="tab-dim-btn" data-dim="uf">Abertura por UF</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Os 4 Quadros -->
    <div class="quad-grid">
      <!-- 1. Market Share -->
      <div class="quad-card">
        <h3>1. MARKET SHARE (%) <span class="sub">participação sobre a base total</span></h3>
        <div class="pbody" style="padding:0">
          <table id="tblResumoShare"></table>
        </div>
      </div>
      <!-- 2. Net Adds -->
      <div class="quad-card">
        <h3>2. NET ADDS (ADIÇÕES LÍQUIDAS) <span class="sub">adições no mês (ago/26)</span></h3>
        <div class="pbody" style="padding:0">
          <table id="tblResumoAdds"></table>
        </div>
      </div>
      <!-- 3. Base de Clientes -->
      <div class="quad-card">
        <h3>3. BASE DE CLIENTES (ACESSOS) <span class="sub">posição ativa em ago/26</span></h3>
        <div class="pbody" style="padding:0">
          <table id="tblResumoBase"></table>
        </div>
      </div>
      <!-- 4. Net Share -->
      <div class="quad-card">
        <h3>4. NET SHARE (%) <span class="sub">participação nas adições líquidas positivas</span></h3>
        <div class="pbody" style="padding:0">
          <table id="tblResumoNetShare"></table>
        </div>
      </div>
    </div>
  </div>

  <!-- VISÃO 2: ISP'S EM 4 QUADRANTES ANALÍTICOS -->
  <div id="viewIsp" class="tab-content" style="display:none">
    <div class="panel" style="margin-bottom:14px">
      <h2>Visão ISP's — Provedores Regionais em 4 Dimensões Analíticas <span class="note">Claro consolidada unificada · Top 10 Provedores em Base, Share %, Adds e MoM</span><button class="hlp" data-h="isp">?</button></h2>
    </div>
    <div class="quad-grid">
      <!-- Quadrante 1: Base -->
      <div class="quad-card">
        <h3>BASE DE CLIENTES (ACESSOS) <span class="sub">ago/25 · jul/26 · ago/26</span></h3>
        <div class="pbody" style="padding:0">
          <table id="tblIspBase"></table>
        </div>
      </div>
      <!-- Quadrante 2: Market Share -->
      <div class="quad-card">
        <h3>MARKET SHARE (%) <span class="sub">ago/25 · jul/26 · ago/26</span></h3>
        <div class="pbody" style="padding:0">
          <table id="tblIspShare"></table>
        </div>
      </div>
      <!-- Quadrante 3: Net Adds -->
      <div class="quad-card">
        <h3>NET ADDS (ADIÇÕES LÍQUIDAS) <span class="sub">ago/25 · jul/26 · ago/26</span></h3>
        <div class="pbody" style="padding:0">
          <table id="tblIspAdds"></table>
        </div>
      </div>
      <!-- Quadrante 4: Variação MoM -->
      <div class="quad-card">
        <h3>VARIAÇÃO MOM (%) <span class="sub">crescimento mês contra mês</span></h3>
        <div class="pbody" style="padding:0">
          <table id="tblIspVarMoM"></table>
        </div>
      </div>
    </div>
  </div>

  <!-- VISÃO 3: POR MUNICÍPIO -->
  <div id="viewMunicipio" class="tab-content" style="display:none">
    <div class="panel">
      <h2>Desempenho por Município Polo <span class="note">Market Share, Net Adds e Base por Operadora nas principais praças</span><button class="hlp" data-h="municipio">?</button></h2>
      <div class="pbody" style="padding-top:0">
        <div class="scroll">
          <table id="tblMunicipio"></table>
        </div>
      </div>
    </div>
  </div>

  <!-- VISÃO 4: DETALHADA HISTÓRICA (MATRIZ 14 MESES COM 4 LINHAS POR OPERADOR + PROJEÇÃO DE ULTRAPASSAGEM + BASE ANALÍTICA) -->
  <div id="viewDetalhada" class="tab-content" style="display:none">
    <!-- Card de Projeção de Ultrapassagem & Liderança -->
    <div class="panel" style="margin-bottom:14px;background:#fffdfa;border-left:4px solid var(--amber)">
      <h2>
        Análise de Liderança de Mercado & Projeção de Ultrapassagem
        <span class="note" id="projSubNote">Posição institucional da Claro frente às operadoras concorrentes e conjuntura do mercado</span>
        <button class="hlp" data-h="projecao">?</button>
      </h2>
      <div class="pbody" style="padding:0">
        <div class="proj-box" id="boxProjecao"></div>
      </div>
    </div>

    <!-- Gráfico de Linha: Evolução Histórica da Base (14 Meses) -->
    <div class="panel" style="margin-bottom:14px">
      <h2>Evolução Histórica da Base por Operadora (14 Meses) <span class="note">Tendência mensal da base jul/25 a ago/26</span><button class="hlp" data-h="grafico">?</button></h2>
      <div class="pbody" style="padding:14px 18px">
        <div id="lineChartLegend" class="chart-legend"></div>
        <div id="lineChartSvgWrap" class="chart-svg-wrap"></div>
      </div>
    </div>

    <!-- Matriz Histórica com 4 Linhas por Operadora e Abertura por DDD -->
    <div class="panel">
      <div style="display:flex;justify-content:space-between;align-items:center;padding:10px 14px;border-bottom:1px solid var(--line2)">
        <h2 style="margin:0;padding:0;border:none">Matriz Detalhada Histórica (14 Meses) <span class="note">Base, Market Share %, Net Adds e Net Share % com abertura por DDD</span></h2>
        <div style="display:flex;gap:8px;align-items:center">
          <button class="btn-toggle-ddd" id="btnToggleAllDdd">Expandir / Recolher Todos os DDDs</button>
          <button class="hlp" data-h="detalhada">?</button>
        </div>
      </div>
      <div class="pbody" style="padding-top:0">
        <div class="scroll">
          <table id="tblDetalhadaHistorica"></table>
        </div>
      </div>
    </div>

    <!-- Base Analítica com Busca e Paginação -->
    <div class="panel" style="margin-top:14px">
      <h2>Registros Analíticos Individuais <span class="note" id="detailRowsNote">registros no cenário ativo</span><button class="hlp" data-h="registros">?</button></h2>
      <div class="pbody">
        <div style="display:flex;gap:10px;margin-bottom:10px;align-items:center">
          <input type="text" id="detailSearch" placeholder="Filtrar por texto nos dados exibidos..." style="padding:5px 10px;border:1px solid var(--line);border-radius:2px;font:12px 'Segoe UI',Arial;width:300px">
          <span style="font-size:11px;color:var(--ink3)" id="detailPageInfo"></span>
        </div>
        <div class="scroll">
          <table id="tblDetalhada"></table>
        </div>
      </div>
    </div>
  </div>

</div>

<!-- MODAL DE AJUDA -->
<div class="modal" id="modalHelp">
  <div class="box">
    <div class="hd">
      <h3 id="helpTitle">Ajuda e Metodologia</h3>
      <button id="helpClose">&times;</button>
    </div>
    <div class="bd" id="helpContent"></div>
  </div>
</div>

<script>
const PAYLOAD = {json_data};
const D = PAYLOAD.dicts;
const ROWS = PAYLOAD.rows;
const MONTHS = PAYLOAD.months;
const POLO_CITIES = PAYLOAD.polo_cities;

const DIM_KEYS = ['servico', 'tipo_cidade', 'uf', 'ddd', 'cidade', 'tipo_cliente', 'tipo_mercado', 'grupo', 'empresa', 'velocidade', 'tecnologia'];
const DIM_COL_IDX = {{
  'cidade': 0, 'grupo': 1, 'empresa': 2, 'ddd': 3, 'uf': 4,
  'servico': 5, 'tipo_cidade': 6, 'tipo_cliente': 7, 'velocidade': 8, 'tecnologia': 9, 'tipo_mercado': 10
}};

const DIM_LABELS = {{
  'servico': 'Serviço',
  'tipo_cidade': 'Tipo de Cidade (Cabo)',
  'uf': 'UF (Estado)',
  'ddd': 'DDD',
  'cidade': 'Município',
  'tipo_cliente': 'Tipo de Cliente',
  'tipo_mercado': 'Mercado (Porte)',
  'grupo': 'Grupo Econômico',
  'empresa': 'Empresa / Provedor',
  'velocidade': 'Faixa de Velocidade',
  'tecnologia': 'Tecnologia'
}};

// Identificadores de Big Telcos e Claro
const CLARO_GRP_ID = D.grupo.findIndex(g => g.toUpperCase() === 'CLARO');
const VIVO_GRP_ID = D.grupo.findIndex(g => g.toUpperCase() === 'VIVO');
const TIM_GRP_ID = D.grupo.findIndex(g => g.toUpperCase() === 'TIM');
const OI_GRP_ID = D.grupo.findIndex(g => g.toUpperCase() === 'OI');
const BIG_TELCOS = new Set([CLARO_GRP_ID, VIVO_GRP_ID, TIM_GRP_ID, OI_GRP_ID].filter(id => id >= 0));

// Estado da Aplicação
let sel = {{}};
let currentTab = 'resumida';
let currentResumoDim = 'ddd'; // 'ddd', 'uf', 'reg'
let currentDddQuick = 'TODOS';

// Formatação
const fmt = n => typeof n === 'number' && !isNaN(n) ? Math.round(n).toLocaleString('pt-BR') : '—';
const pct = (a, b, d = 1) => {{
  if (!b || isNaN(b) || b === 0) return '—';
  const val = (100 * a / b);
  return (val >= 0 ? '+' : '') + val.toFixed(d).replace('.', ',') + '%';
}};
const pctAbs = (a, b, d = 1) => {{
  if (!b || isNaN(b) || b === 0) return '—';
  return (100 * a / b).toFixed(d).replace('.', ',') + '%';
}};
const pp = (val, d = 2) => {{
  if (val === null || val === undefined || isNaN(val)) return '—';
  const s = val >= 0 ? '+' + val.toFixed(d).replace('.', ',') : val.toFixed(d).replace('.', ',');
  return s + ' p.p.';
}};

/* ============ Filtro e Cascata Dependente (refreshAvailability) ============ */
function refreshAvailability() {{
  const actDims = Object.keys(sel);
  const av = {{}};
  DIM_KEYS.forEach(k => {{ av[k] = new Set(); }});

  const nRows = ROWS.length;
  for (let r = 0; r < nRows; r++) {{
    const row = ROWS[r];
    let miss = 0;
    let missDim = null;
    for (let k = 0; k < actDims.length; k++) {{
      const dim = actDims[k];
      const colIdx = DIM_COL_IDX[dim];
      const valId = row[colIdx];
      if (!sel[dim].has(valId)) {{
        miss++;
        if (miss > 1) break;
        missDim = dim;
      }}
    }}
    if (miss === 0) {{
      for (let k = 0; k < DIM_KEYS.length; k++) {{
        const dim = DIM_KEYS[k];
        av[dim].add(row[DIM_COL_IDX[dim]]);
      }}
    }} else if (miss === 1 && missDim && av[missDim]) {{
      av[missDim].add(row[DIM_COL_IDX[missDim]]);
    }}
  }}

  DIM_KEYS.forEach(dim => {{
    const s = document.querySelector(`select[data-dim="${{dim}}"]`);
    if (!s) return;
    const A = av[dim];
    const opts = [...s.options];
    let nAvail = 0;
    opts.forEach(o => {{
      const has = A.has(+o.value);
      o.classList.toggle('na', !has);
      o.disabled = !has && !o.selected;
      o._ok = has;
      if (has) nAvail++;
    }});

    const key = o => o.textContent.toLowerCase();
    const ok = opts.filter(o => o._ok).sort((a, b) => key(a).localeCompare(key(b), 'pt-BR'));
    const na = opts.filter(o => !o._ok).sort((a, b) => key(a).localeCompare(key(b), 'pt-BR'));
    const ord = ok.concat(na);

    let orderChanged = false;
    for (let i = 0; i < ord.length; i++) {{
      if (opts[i] !== ord[i]) {{ orderChanged = true; break; }}
    }}
    if (orderChanged) {{
      const frag = document.createDocumentFragment();
      ord.forEach(o => frag.appendChild(o));
      s.appendChild(frag);
    }}

    const nt = document.getElementById('na_' + dim);
    if (nt) {{
      nt.textContent = nAvail < opts.length ? `${{nAvail}} de ${{opts.length}} disponíveis · indisponíveis ao final` : '';
    }}
  }});
}}

function getFilteredRows() {{
  const actDims = Object.keys(sel);
  if (!actDims.length) return ROWS;
  const res = [];
  const nRows = ROWS.length;
  for (let r = 0; r < nRows; r++) {{
    const row = ROWS[r];
    let ok = true;
    for (let k = 0; k < actDims.length; k++) {{
      const dim = actDims[k];
      const colIdx = DIM_COL_IDX[dim];
      if (!sel[dim].has(row[colIdx])) {{
        ok = false;
        break;
      }}
    }}
    if (ok) res.push(row);
  }}
  return res;
}}

/* ============ Gaveta de Filtros UI ============ */
function buildFilterUI() {{
  const fEl = document.getElementById('filters');
  fEl.innerHTML = '';

  DIM_KEYS.forEach(dim => {{
    const lab = DIM_LABELS[dim];
    const div = document.createElement('div');
    div.className = 'f';
    let vals = D[dim].map((v, i) => [v, i]);
    vals.sort((a, b) => a[0].localeCompare(b[0], 'pt-BR'));

    div.innerHTML = `
      <label>${{lab}}<span class="cnt">${{D[dim].length}}</span></label>
      <div class="frow">
        <input type="text" placeholder="buscar…" data-s="${{dim}}">
        <button class="fbtn" data-all="${{dim}}" title="Selecionar tudo que está visível">T</button>
        <button class="fbtn" data-clr="${{dim}}" title="Limpar este filtro">×</button>
      </div>
      <select multiple data-dim="${{dim}}">${{vals.map(([v, i]) => `<option value="${{i}}">${{v}}</option>`).join('')}}</select>
      <div class="sel" id="sel_${{dim}}"></div>
      <div class="na-note" id="na_${{dim}}"></div>
    `;
    fEl.appendChild(div);
  }});

  // Eventos de Busca
  fEl.querySelectorAll('input[data-s]').forEach(inp => {{
    inp.oninput = () => {{
      const dim = inp.dataset.s, q = inp.value.trim().toLowerCase();
      const s = fEl.querySelector(`select[data-dim="${{dim}}"]`);
      let vis = 0;
      [...s.options].forEach(o => {{
        const hit = (!q || o.textContent.toLowerCase().includes(q)) && !o.disabled;
        o.hidden = !hit;
        if (hit) vis++;
      }});
      const btn = fEl.querySelector(`button[data-all="${{dim}}"]`);
      btn.classList.toggle('act', !!q);
      btn.title = q ? `Selecionar ${{vis}} itens visíveis` : 'Selecionar tudo que está visível';
    }};
    inp.onkeydown = e => {{
      if (e.key === 'Enter') {{
        e.preventDefault();
        fEl.querySelector(`button[data-all="${{inp.dataset.s}}"]`).click();
      }}
    }};
  }});

  // Botão T (selecionar visíveis)
  fEl.querySelectorAll('button[data-all]').forEach(b => {{
    b.onclick = () => {{
      const s = fEl.querySelector(`select[data-dim="${{b.dataset.all}}"]`);
      [...s.options].forEach(o => {{
        if (!o.hidden && !o.disabled) o.selected = true;
      }});
      readFiltersFromUI();
      render();
    }};
  }});

  // Botão × (limpar individual)
  fEl.querySelectorAll('button[data-clr]').forEach(b => {{
    b.onclick = () => {{
      const dim = b.dataset.clr;
      const s = fEl.querySelector(`select[data-dim="${{dim}}"]`);
      [...s.options].forEach(o => {{ o.selected = false; o.hidden = false; }});
      const inp = fEl.querySelector(`input[data-s="${{dim}}"]`);
      if (inp) inp.value = '';
      delete sel[dim];
      if (dim === 'ddd') syncDddPills();
      render();
    }};
  }});

  // Mudança em multiselect
  fEl.addEventListener('change', e => {{
    if (e.target.tagName === 'SELECT') {{
      readFiltersFromUI();
      if (e.target.dataset.dim === 'ddd') syncDddPills();
      render();
    }}
  }});

  // Toggle Gaveta
  const dr = document.getElementById('fDrawer'), bt = document.getElementById('btnDrawer');
  function toggleDrawer(force) {{
    const open = force !== undefined ? force : dr.style.display === 'none';
    dr.style.display = open ? '' : 'none';
    bt.classList.toggle('open', open);
  }}
  bt.onclick = e => {{ e.stopPropagation(); toggleDrawer(); }};
  document.getElementById('fToggleBar').onclick = e => {{
    if (e.target.closest('.hlp') || e.target.closest('.drawer-btn')) return;
    toggleDrawer();
  }};

  document.getElementById('btnApply').onclick = () => {{
    readFiltersFromUI();
    render();
    toggleDrawer(false);
  }};

  document.getElementById('btnClear').onclick = () => {{
    applyDefaultFilters();
    render();
  }};

  document.getElementById('btnClearAll').onclick = () => {{
    sel = {{}};
    fEl.querySelectorAll('select').forEach(s => [...s.options].forEach(o => {{ o.selected = false; o.hidden = false; }}));
    fEl.querySelectorAll('input[data-s]').forEach(i => {{ i.value = ''; }});
    syncDddPills();
    render();
  }};

  document.getElementById('btnCsv').onclick = exportCsv;
}}

function applyDefaultFilters() {{
  sel = {{}};
  const fEl = document.getElementById('filters');
  fEl.querySelectorAll('select').forEach(s => [...s.options].forEach(o => {{ o.selected = false; o.hidden = false; }}));
  fEl.querySelectorAll('input[data-s]').forEach(i => {{ i.value = ''; }});

  // Pre-set padrão oficial: Banda Larga (02.BL) + Tipo de Cidade: GPON e HFC (Tecnologia desmarcada)
  const blIdx = D.servico.indexOf('02.BL');
  if (blIdx >= 0) {{
    sel.servico = new Set([blIdx]);
    const s = document.querySelector('select[data-dim="servico"]');
    if (s) [...s.options].forEach(o => {{ if (+o.value === blIdx) o.selected = true; }});
  }}

  const tcIds = [];
  D.tipo_cidade.forEach((t, idx) => {{
    const upper = t.toUpperCase().trim();
    if (upper === 'GPON' || upper === 'HFC') {{
      tcIds.push(idx);
    }}
  }});
  if (tcIds.length) {{
    sel.tipo_cidade = new Set(tcIds);
    const s = document.querySelector('select[data-dim="tipo_cidade"]');
    if (s) [...s.options].forEach(o => {{ if (tcIds.includes(+o.value)) o.selected = true; }});
  }}

  // Tecnologia permanece desmarcada (todas disponíveis sem filtro restritivo de tecnologia)
  delete sel.tecnologia;
  const sTec = document.querySelector('select[data-dim="tecnologia"]');
  if (sTec) [...sTec.options].forEach(o => {{ o.selected = false; }});

  syncDddPills();
}}

function readFiltersFromUI() {{
  DIM_KEYS.forEach(dim => {{
    const s = document.querySelector(`select[data-dim="${{dim}}"]`);
    if (!s) return;
    const ch = [...s.selectedOptions].map(o => +o.value);
    if (!ch.length) {{
      delete sel[dim];
    }} else {{
      sel[dim] = new Set(ch);
    }}
  }});
}}

function updateSelCounts() {{
  DIM_KEYS.forEach(dim => {{
    const sp = document.getElementById('sel_' + dim);
    if (!sp) return;
    const n = sel[dim] ? sel[dim].size : 0;
    sp.textContent = n ? n + ' selecionado' + (n > 1 ? 's' : '') : '';
  }});
}}

function syncDddPills() {{
  const pills = document.querySelectorAll('.ddd-pill');
  pills.forEach(p => p.classList.remove('act'));
  if (!sel.ddd || sel.ddd.size === 0) {{
    document.querySelector('.ddd-pill[data-ddd="TODOS"]')?.classList.add('act');
  }} else if (sel.ddd.size === 1) {{
    const dVal = D.ddd[[...sel.ddd][0]];
    const pill = document.querySelector(`.ddd-pill[data-ddd="${{dVal}}"]`);
    if (pill) pill.classList.add('act');
  }}
}}

function drawChips() {{
  const cEl = document.getElementById('chips');
  cEl.innerHTML = '';
  const act = Object.keys(sel);
  if (!act.length) {{
    cEl.innerHTML = '<span style="font-size:11px;color:var(--ink3);font-style:italic">Todos os serviços e tecnologias (sem filtros)</span>';
    return;
  }}
  act.forEach(dim => {{
    const arr = [...sel[dim]].map(id => D[dim][id]);
    const lab = DIM_LABELS[dim];
    const chip = document.createElement('span');
    chip.className = 'chip';
    chip.textContent = `${{lab}}: ${{arr.length > 2 ? arr.slice(0, 2).join(', ') + ' +' + (arr.length - 2) : arr.join(', ')}}`;
    cEl.appendChild(chip);
  }});
}}

function drawSummary() {{
  const sEl = document.getElementById('fSummary');
  const act = Object.keys(sel);
  if (!act.length) {{
    sEl.textContent = 'todos os serviços e tecnologias (visão irrestrita)';
  }} else {{
    const isDefault = act.length === 2 && sel.servico && sel.tipo_cidade && !sel.tecnologia && !sel.cidade && !sel.ddd && !sel.uf;
    if (isDefault) {{
      sEl.textContent = 'padrão ativo: Banda Larga (02.BL) · Tipo de Cidade: GPON + HFC';
    }} else {{
      const parts = act.map(dim => `${{DIM_LABELS[dim]}} (${{sel[dim].size}})`);
      sEl.textContent = `filtros ativos: ${{parts.join(', ')}}`;
    }}
  }}
}}

/* ============ Renderização Principal ============ */
function render() {{
  updateSelCounts();
  refreshAvailability();
  drawChips();
  drawSummary();

  const fRows = getFilteredRows();
  document.getElementById('hdrRows').textContent = `${{fRows.length.toLocaleString('pt-BR')}} registros`;

  renderKpis(fRows);

  if (currentTab === 'resumida') renderResumida(fRows);
  else if (currentTab === 'isp') renderISPs(fRows);
  else if (currentTab === 'municipio') renderMunicipio(fRows);
  else if (currentTab === 'detalhada') renderDetalhada(fRows);
}}

/* ============ KPIs ============ */
function renderKpis(fRows) {{
  let claroAgo25 = 0, claroJul26 = 0, claroAgo26 = 0, claroJun26 = 0;
  let totAgo25 = 0, totJul26 = 0, totAgo26 = 0, totJun26 = 0;
  let entitiesAgo26 = {{}};

  for (let i = 0; i < fRows.length; i++) {{
    const r = fRows[i];
    const grpId = r[1];
    const empId = r[2];
    const empName = D.empresa[empId];
    const m = r[11];
    const vAgo25 = m[1], vJun26 = m[11], vJul26 = m[12], vAgo26 = m[13];

    totAgo25 += vAgo25; totJun26 += vJun26; totJul26 += vJul26; totAgo26 += vAgo26;

    const isClaro = (grpId === CLARO_GRP_ID || empName.toUpperCase().startsWith('CLARO'));
    if (isClaro) {{
      claroAgo25 += vAgo25; claroJun26 += vJun26; claroJul26 += vJul26; claroAgo26 += vAgo26;
    }}

    // Entidade competidora individual (Claro, Vivo, Tim, Oi, Sky ou empresa ISP individual)
    let entKey = 'CLARO';
    if (!isClaro) {{
      if (grpId === VIVO_GRP_ID) entKey = 'VIVO';
      else if (grpId === TIM_GRP_ID) entKey = 'TIM';
      else if (grpId === OI_GRP_ID) entKey = 'OI';
      else if (D.grupo[grpId].includes('SKY') || D.grupo[grpId].includes('WERTHEIN')) entKey = 'SKY';
      else entKey = empName;
    }}
    if (!entitiesAgo26[entKey]) entitiesAgo26[entKey] = {{ baseA: 0, baseJ: 0 }};
    entitiesAgo26[entKey].baseA += vAgo26;
    entitiesAgo26[entKey].baseJ += vJul26;
  }}

  // Ordena concorrentes por base de assinantes
  const sortedEntities = Object.entries(entitiesAgo26).sort((a, b) => b[1].baseA - a[1].baseA);
  const claroRank = sortedEntities.findIndex(x => x[0] === 'CLARO') + 1;
  const isLeader = totAgo26 > 0 && claroAgo26 > 0 && claroRank === 1;

  const leaderEnt = sortedEntities[0] || ['CLARO', {{ baseA: claroAgo26, baseJ: claroJul26 }}];
  const secondEnt = sortedEntities[1] || leaderEnt;

  // Se Claro é líder, o concorrente de comparação é a 2ª colocada; senão, é a líder
  const rivalName = isLeader ? secondEnt[0] : (sortedEntities[0] ? sortedEntities[0][0] : '—');
  const rivalBase = isLeader ? secondEnt[1].baseA : (sortedEntities[0] ? sortedEntities[0][1].baseA : 0);
  const gapClaro = isLeader ? (claroAgo26 - rivalBase) : (claroAgo26 - rivalBase);

  const shareAgo26 = totAgo26 > 0 ? (claroAgo26 / totAgo26) * 100 : 0;
  const shareJul26 = totJul26 > 0 ? (claroJul26 / totJul26) * 100 : 0;
  const shareAgo25 = totAgo25 > 0 ? (claroAgo25 / totAgo25) * 100 : 0;

  const varMoM_pp = shareAgo26 - shareJul26;
  const varYoY_pct = claroAgo25 > 0 ? ((claroAgo26 - claroAgo25) / claroAgo25) * 100 : 0;

  const netAddsClaro = claroAgo26 - claroJul26;
  
  // Net Share oficial: soma das adições estritamente positivas das entidades
  let posAddsSum = 0;
  for (const ent in entitiesAgo26) {{
    const net = entitiesAgo26[ent].baseA - entitiesAgo26[ent].baseJ;
    if (net > 0) posAddsSum += net;
  }}
  const netShareClaro = (posAddsSum > 0 && netAddsClaro > 0) ? (netAddsClaro / posAddsSum) * 100 : 0;

  let posLabel = '1º Lugar (Líder)';
  let posDesc = 'Liderança absoluta consolidada';
  let gapLabel = 'Vantagem sobre 2ª Colocada';
  let gapVal = '+' + fmt(gapClaro);
  let gapDesc = 'sobre ' + rivalName + ' (' + fmt(rivalBase) + ')';

  if (totAgo26 === 0) {{
    posLabel = 'Sem Rede Cabeada';
    posDesc = 'Não há rede GPON/HFC ativa neste recorte';
    gapLabel = 'Gap para a Liderança';
    gapVal = '—';
    gapDesc = 'Sem operadoras cabeadas ativas';
  }} else if (claroAgo26 === 0) {{
    posLabel = claroRank > 0 ? `${{claroRank}}º Lugar (Sem Base)` : 'Sem Presença';
    posDesc = 'Líder: ' + rivalName + ' (' + fmt(rivalBase) + ')';
    gapLabel = 'Gap para a Liderança';
    gapVal = fmt(gapClaro);
    gapDesc = 'para ' + rivalName + ' (' + fmt(rivalBase) + ')';
  }} else if (!isLeader) {{
    posLabel = claroRank + 'º Lugar';
    posDesc = 'Líder: ' + rivalName + ' (' + fmt(rivalBase) + ')';
    gapLabel = 'Gap para a Liderança';
    gapVal = fmt(gapClaro);
    gapDesc = 'para ' + rivalName + ' (' + fmt(rivalBase) + ')';
  }}

  const kEl = document.getElementById('kpis');
  kEl.innerHTML = `
    <div class="kpi acc">
      <div class="k">Market Share Claro</div>
      <div class="v">${{shareAgo26.toFixed(1).replace('.', ',')}}%</div>
      <div class="d">ago/26 sobre a base total</div>
    </div>
    <div class="kpi ${{varMoM_pp >= 0 ? 'green' : 'acc'}}">
      <div class="k">Variação MoM</div>
      <div class="v">${{pp(varMoM_pp)}}</div>
      <div class="d">vs. jul/26 (${{shareJul26.toFixed(1).replace('.', ',')}}%)</div>
    </div>
    <div class="kpi ${{varYoY_pct >= 0 ? 'green' : 'acc'}}">
      <div class="k">Crescimento YoY (Base)</div>
      <div class="v">${{varYoY_pct >= 0 ? '+' : ''}}${{varYoY_pct.toFixed(1).replace('.', ',')}}%</div>
      <div class="d">vs. ago/25 (${{fmt(claroAgo25)}})</div>
    </div>
    <div class="kpi">
      <div class="k">Posição de Mercado</div>
      <div class="v">${{posLabel}}</div>
      <div class="d">${{posDesc}}</div>
    </div>
    <div class="kpi">
      <div class="k">${{gapLabel}}</div>
      <div class="v">${{gapVal}}</div>
      <div class="d">${{gapDesc}}</div>
    </div>
    <div class="kpi">
      <div class="k">Net Adds no Mês</div>
      <div class="v ${{netAddsClaro >= 0 ? 'pos' : 'neg'}}">${{netAddsClaro >= 0 ? '+' : ''}}${{fmt(netAddsClaro)}}</div>
      <div class="d">Adições líquidas ago/26</div>
    </div>
    <div class="kpi">
      <div class="k">Net Share Claro</div>
      <div class="v">${{netShareClaro > 0 ? netShareClaro.toFixed(1).replace('.', ',') + '%' : '0,0%'}}</div>
      <div class="d">Participação nas adições positivas</div>
    </div>
  `;
}}

/* ============ VISÃO 1: RESUMIDA (4 QUADROS COMPARATIVOS + SELETOR DE DIMENSÃO) ============ */
function renderResumida(fRows) {{
  const PLAYERS = ['CLARO', 'VIVO', 'TIM', 'OI', 'SKY', 'OUTROS'];
  
  // Determina linhas da dimensão selecionada (DDD ou UF)
  let dimItems = [];
  if (currentResumoDim === 'uf') {{
    dimItems = ['AM', 'AP', 'MA', 'PA', 'RR'].map(u => ({{ key: u, label: 'UF ' + u }}));
  }} else {{
    dimItems = ['91', '92', '93', '94', '95', '96', '97', '98', '99'].map(d => ({{ key: d, label: 'DDD ' + d }}));
  }}

  // Estrutura de agregação
  const aggData = {{}};
  dimItems.forEach(it => {{
    aggData[it.key] = {{
      baseA26: {{ CLARO: 0, VIVO: 0, TIM: 0, OI: 0, SKY: 0, OUTROS: 0 }},
      baseJ26: {{ CLARO: 0, VIVO: 0, TIM: 0, OI: 0, SKY: 0, OUTROS: 0 }},
      ispsA26: {{}},
      ispsJ26: {{}},
      totA26: 0,
      totJ26: 0
    }};
  }});

  const totalGeral = {{
    baseA26: {{ CLARO: 0, VIVO: 0, TIM: 0, OI: 0, SKY: 0, OUTROS: 0 }},
    baseJ26: {{ CLARO: 0, VIVO: 0, TIM: 0, OI: 0, SKY: 0, OUTROS: 0 }},
    ispsA26: {{}},
    ispsJ26: {{}},
    totA26: 0,
    totJ26: 0
  }};

  for (let i = 0; i < fRows.length; i++) {{
    const r = fRows[i];
    const grpId = r[1];
    const empId = r[2];
    const empName = D.empresa[empId];
    const dddStr = D.ddd[r[3]];
    const ufStr = D.uf[r[4]];
    const m = r[11];
    const j26 = m[12], a26 = m[13];

    let rowKey = null;
    if (currentResumoDim === 'ddd') rowKey = dddStr;
    else if (currentResumoDim === 'uf') rowKey = ufStr;
    else rowKey = 'RNO';

    const obj = aggData[rowKey];
    if (!obj) continue;

    const isClaro = (grpId === CLARO_GRP_ID || empName.toUpperCase().startsWith('CLARO'));
    let pKey = 'OUTROS';
    if (isClaro) pKey = 'CLARO';
    else if (grpId === VIVO_GRP_ID) pKey = 'VIVO';
    else if (grpId === TIM_GRP_ID) pKey = 'TIM';
    else if (grpId === OI_GRP_ID) pKey = 'OI';
    else if (D.grupo[grpId].includes('SKY') || D.grupo[grpId].includes('WERTHEIN')) pKey = 'SKY';
    else {{
      obj.ispsA26[empName] = (obj.ispsA26[empName] || 0) + a26;
      obj.ispsJ26[empName] = (obj.ispsJ26[empName] || 0) + j26;
    }}

    obj.baseA26[pKey] += a26;
    obj.baseJ26[pKey] += j26;
    obj.totA26 += a26;
    obj.totJ26 += j26;

    if (currentResumoDim !== 'reg') {{
      totalGeral.baseA26[pKey] += a26;
      totalGeral.baseJ26[pKey] += j26;
      totalGeral.totA26 += a26;
      totalGeral.totJ26 += j26;
      if (pKey === 'OUTROS') {{
        totalGeral.ispsA26[empName] = (totalGeral.ispsA26[empName] || 0) + a26;
        totalGeral.ispsJ26[empName] = (totalGeral.ispsJ26[empName] || 0) + j26;
      }}
    }}
  }}

  // Se for visão regional, o Total Brasil soma todas as 10 regionais
  if (currentResumoDim === 'reg') {{
    dimItems.forEach(it => {{
      const d = aggData[it.key];
      PLAYERS.forEach(p => {{
        totalGeral.baseA26[p] += d.baseA26[p];
        totalGeral.baseJ26[p] += d.baseJ26[p];
      }});
      totalGeral.totA26 += d.totA26;
      totalGeral.totJ26 += d.totJ26;
    }});
  }}

  // Função auxiliar para calcular e desenhar cada tabela dos 4 quadros
  function buildQuadroTable(metricType) {{
    let html = `<thead><tr>
      <th class="l">${{currentResumoDim === 'ddd' ? 'DDD' : (currentResumoDim === 'uf' ? 'UF' : 'Regional')}}</th>
      <th>CLARO</th><th>VIVO</th><th>TIM</th><th>OI</th><th>SKY</th><th>OUTROS</th>
      <th style="text-align:center">Posição Claro</th>
    </tr></thead><tbody>`;

    const allRows = [...dimItems];
    allRows.push({{ key: 'TOTAL', label: currentResumoDim === 'reg' ? 'Total Brasil' : 'Total Regional' }});

    allRows.forEach(it => {{
      const d = it.key === 'TOTAL' ? totalGeral : aggData[it.key];
      const isTotalRow = it.key === 'TOTAL';

      // Monta os valores de cada player na linha
      const rowVals = {{}};
      // Soma dos adds estritamente positivos dos players
      let posNetSum = 0;
      PLAYERS.forEach(p => {{
        const net = d.baseA26[p] - d.baseJ26[p];
        if (net > 0) posNetSum += net;
      }});

      PLAYERS.forEach(p => {{
        const bA = d.baseA26[p], bJ = d.baseJ26[p];
        const net = bA - bJ;
        if (metricType === 'share') {{
          rowVals[p] = d.totA26 > 0 ? (bA / d.totA26 * 100) : 0;
        }} else if (metricType === 'adds') {{
          rowVals[p] = net;
        }} else if (metricType === 'base') {{
          rowVals[p] = bA;
        }} else if (metricType === 'net_share') {{
          rowVals[p] = (posNetSum > 0 && net > 0) ? (net / posNetSum * 100) : 0;
        }}
      }});

      // Determina posição da Claro na linha:
      // O concorrente do grupo Outros considerado é o maior ISP individual (e não o agrupamento de 300 ISPs)
      let maxIspVal = 0;
      if (d.ispsA26 && Object.keys(d.ispsA26).length > 0) {{
        if (metricType === 'base') maxIspVal = Math.max(...Object.values(d.ispsA26));
        else if (metricType === 'share') {{
          const mb = Math.max(...Object.values(d.ispsA26));
          maxIspVal = d.totA26 > 0 ? (mb / d.totA26 * 100) : 0;
        }} else if (metricType === 'adds') {{
          const ispNets = Object.keys(d.ispsA26).map(e => d.ispsA26[e] - (d.ispsJ26[e] || 0));
          maxIspVal = ispNets.length ? Math.max(...ispNets) : 0;
        }} else if (metricType === 'net_share') {{
          const ispNets = Object.keys(d.ispsA26).map(e => d.ispsA26[e] - (d.ispsJ26[e] || 0));
          const maxNet = ispNets.length ? Math.max(...ispNets) : 0;
          maxIspVal = (posNetSum > 0 && maxNet > 0) ? (maxNet / posNetSum * 100) : 0;
        }}
      }} else {{
        // Benchmark regional estimado
        maxIspVal = rowVals['OUTROS'] * 0.30;
      }}

      // Concorrentes individuais para ranking da Claro:
      const compEnts = [
        {{ p: 'CLARO', v: rowVals['CLARO'] }},
        {{ p: 'VIVO', v: rowVals['VIVO'] }},
        {{ p: 'TIM', v: rowVals['TIM'] }},
        {{ p: 'OI', v: rowVals['OI'] }},
        {{ p: 'SKY', v: rowVals['SKY'] }},
        {{ p: 'MAX_ISP', v: maxIspVal }}
      ].sort((a, b) => b.v - a.v);

      const claroRank = compEnts.findIndex(x => x.p === 'CLARO') + 1;
      const posClass = claroRank === 1 ? 'pos-1' : (claroRank === 2 ? 'pos-2' : (claroRank === 3 ? 'pos-3' : 'pos-other'));

      // Melhor player individual da linha
      const bestPlayer = compEnts[0].p === 'MAX_ISP' ? 'OUTROS' : compEnts[0].p;
      const bestVal = rowVals[bestPlayer];

      html += `<tr class="${{isTotalRow ? 'total-row' : ''}}">
        <td class="l"><b>${{it.label}}</b></td>`;

      PLAYERS.forEach(p => {{
        const v = rowVals[p];
        const isBest = (p === bestPlayer && bestVal > 0);
        let cellText = '—';
        let cellClass = isBest ? 'best-val' : '';

        if (metricType === 'share' || metricType === 'net_share') {{
          cellText = v > 0 ? v.toFixed(1).replace('.', ',') + '%' : '0,0%';
        }} else if (metricType === 'adds') {{
          cellText = (v >= 0 ? '+' : '') + fmt(v);
          if (!isBest) cellClass = v >= 0 ? 'pos' : 'neg';
        }} else if (metricType === 'base') {{
          cellText = fmt(v);
        }}

        html += `<td class="${{cellClass}}">${{cellText}}</td>`;
      }});

      html += `<td style="text-align:center"><span class="pos-badge ${{posClass}}">${{claroRank}}º Lugar</span></td></tr>`;
    }});

    html += '</tbody>';
    return html;
  }}

  document.getElementById('tblResumoShare').innerHTML = buildQuadroTable('share');
  document.getElementById('tblResumoAdds').innerHTML = buildQuadroTable('adds');
  document.getElementById('tblResumoBase').innerHTML = buildQuadroTable('base');
  document.getElementById('tblResumoNetShare').innerHTML = buildQuadroTable('net_share');
}}

/* ============ VISÃO 2: ISP'S EM 4 QUADRANTES ANALÍTICOS ============ */
function renderISPs(fRows) {{
  const totalMercado = [0, 0, 0, 0, 0]; // jul25, ago25, jun26, jul26, ago26
  const claroTot = [0, 0, 0, 0, 0];
  const ispTot = [0, 0, 0, 0, 0];
  const ispsMap = new Map();

  for (let i = 0; i < fRows.length; i++) {{
    const r = fRows[i];
    const grpId = r[1];
    const empId = r[2];
    const m = r[11];
    const v0 = m[0], v1 = m[1], v2 = m[11], v3 = m[12], v4 = m[13];

    totalMercado[0] += v0; totalMercado[1] += v1;
    totalMercado[2] += v2; totalMercado[3] += v3; totalMercado[4] += v4;

    const isClaro = (grpId === CLARO_GRP_ID || D.empresa[empId].toUpperCase().startsWith('CLARO'));
    if (isClaro) {{
      claroTot[0] += v0; claroTot[1] += v1;
      claroTot[2] += v2; claroTot[3] += v3; claroTot[4] += v4;
    }}

    const isBig = BIG_TELCOS.has(grpId) || isClaro;
    if (!isBig) {{
      ispTot[0] += v0; ispTot[1] += v1;
      ispTot[2] += v2; ispTot[3] += v3; ispTot[4] += v4;

      let eArr = ispsMap.get(empId);
      if (!eArr) {{
        eArr = [0, 0, 0, 0, 0];
        ispsMap.set(empId, eArr);
      }}
      eArr[0] += v0; eArr[1] += v1;
      eArr[2] += v2; eArr[3] += v3; eArr[4] += v4;
    }}
  }}

  // Top 10 ISPs por ago/26
  const sortedISPs = Array.from(ispsMap.entries())
    .sort((a, b) => b[1][4] - a[1][4])
    .slice(0, 10);

  const rowsList = [];
  rowsList.push({{ name: 'CLARO', vals: claroTot, isClaro: true, isTotal: false }});
  rowsList.push({{ name: "TOTAL ISP'S", vals: ispTot, isClaro: false, isTotal: true }});
  sortedISPs.forEach(([empId, vals]) => {{
    rowsList.push({{ name: D.empresa[empId], vals: vals, isClaro: false, isTotal: false }});
  }});

  // 1. Tabela Base
  let tBase = '<thead><tr><th class="l">TOP 10 ISPs</th><th>ago/25</th><th>jul/26</th><th>ago/26</th><th>MoM</th><th>YoY</th><th>Part. ISP</th></tr></thead><tbody>';
  rowsList.forEach(r => {{
    const [j25, a25, jn26, j26, a26] = r.vals;
    let partIsp = '—';
    if (r.isClaro) {{
      partIsp = totalMercado[4] > 0 ? (a26 / totalMercado[4] * 100).toFixed(1).replace('.', ',') + '%' : '—';
    }} else if (r.isTotal) {{
      partIsp = '100,0%';
    }} else {{
      partIsp = ispTot[4] > 0 ? (a26 / ispTot[4] * 100).toFixed(1).replace('.', ',') + '%' : '—';
    }}

    const rClass = r.isClaro ? 'claro-row' : (r.isTotal ? 'isp-tot-row' : '');
    tBase += `<tr class="${{rClass}}">
      <td class="l">${{r.name}}</td>
      <td>${{fmt(a25)}}</td>
      <td>${{fmt(j26)}}</td>
      <td>${{fmt(a26)}}</td>
      <td>${{pct(a26 - j26, j26)}}</td>
      <td>${{pct(a26 - a25, a25)}}</td>
      <td>${{partIsp}}</td>
    </tr>`;
  }});
  tBase += '</tbody>';
  document.getElementById('tblIspBase').innerHTML = tBase;

  // 2. Tabela Market Share
  let tShare = '<thead><tr><th class="l">TOP 10 ISPs</th><th>ago/25</th><th>jul/26</th><th>ago/26</th><th>MoM</th><th>YoY</th></tr></thead><tbody>';
  rowsList.forEach(r => {{
    const [j25, a25, jn26, j26, a26] = r.vals;
    const sA25 = totalMercado[1] > 0 ? (a25 / totalMercado[1]) * 100 : 0;
    const sJ26 = totalMercado[3] > 0 ? (j26 / totalMercado[3]) * 100 : 0;
    const sA26 = totalMercado[4] > 0 ? (a26 / totalMercado[4]) * 100 : 0;

    const rClass = r.isClaro ? 'claro-row' : (r.isTotal ? 'isp-tot-row' : '');
    tShare += `<tr class="${{rClass}}">
      <td class="l">${{r.name}}</td>
      <td>${{sA25.toFixed(2).replace('.', ',')}}%</td>
      <td>${{sJ26.toFixed(2).replace('.', ',')}}%</td>
      <td>${{sA26.toFixed(2).replace('.', ',')}}%</td>
      <td>${{pp(sA26 - sJ26)}}</td>
      <td>${{pp(sA26 - sA25)}}</td>
    </tr>`;
  }});
  tShare += '</tbody>';
  document.getElementById('tblIspShare').innerHTML = tShare;

  // 3. Tabela Net Adds
  let tAdds = '<thead><tr><th class="l">TOP 10 ISPs</th><th>ago/25</th><th>jul/26</th><th>ago/26</th><th>MoM</th><th>YoY</th></tr></thead><tbody>';
  rowsList.forEach(r => {{
    const [j25, a25, jn26, j26, a26] = r.vals;
    const netA25 = a25 - j25;
    const netJ26 = j26 - jn26;
    const netA26 = a26 - j26;

    const rClass = r.isClaro ? 'claro-row' : (r.isTotal ? 'isp-tot-row' : '');
    tAdds += `<tr class="${{rClass}}">
      <td class="l">${{r.name}}</td>
      <td>${{fmt(netA25)}}</td>
      <td>${{fmt(netJ26)}}</td>
      <td>${{fmt(netA26)}}</td>
      <td>${{netA26 - netJ26 >= 0 ? '+' : ''}}${{fmt(netA26 - netJ26)}}</td>
      <td>${{netA26 - netA25 >= 0 ? '+' : ''}}${{fmt(netA26 - netA25)}}</td>
    </tr>`;
  }});
  tAdds += '</tbody>';
  document.getElementById('tblIspAdds').innerHTML = tAdds;

  // 4. Tabela Variação MoM %
  let tVarMoM = '<thead><tr><th class="l">TOP 10 ISPs</th><th>ago/25</th><th>jul/26</th><th>ago/26</th><th>MoM</th><th>YoY</th></tr></thead><tbody>';
  rowsList.forEach(r => {{
    const [j25, a25, jn26, j26, a26] = r.vals;
    const vA25 = j25 > 0 ? ((a25 - j25) / j25) * 100 : 0;
    const vJ26 = jn26 > 0 ? ((j26 - jn26) / jn26) * 100 : 0;
    const vA26 = j26 > 0 ? ((a26 - j26) / j26) * 100 : 0;

    const rClass = r.isClaro ? 'claro-row' : (r.isTotal ? 'isp-tot-row' : '');
    tVarMoM += `<tr class="${{rClass}}">
      <td class="l">${{r.name}}</td>
      <td>${{pct(a25 - j25, j25)}}</td>
      <td>${{pct(j26 - jn26, jn26)}}</td>
      <td>${{pct(a26 - j26, j26)}}</td>
      <td>${{pp(vA26 - vJ26)}}</td>
      <td>${{pp(vA26 - vA25)}}</td>
    </tr>`;
  }});
  tVarMoM += '</tbody>';
  document.getElementById('tblIspVarMoM').innerHTML = tVarMoM;
}}

/* ============ VISÃO 3: POR MUNICÍPIO ============ */
function renderMunicipio(fRows) {{
  const tEl = document.getElementById('tblMunicipio');
  const cityAgg = {{}};

  for (let i = 0; i < fRows.length; i++) {{
    const r = fRows[i];
    const cidStr = D.cidade[r[0]];
    const ufStr = D.uf[r[4]];
    const mercadoStr = D.tipo_mercado[r[10]];
    const key = ufStr + ' - ' + cidStr;

    if (!cityAgg[key]) {{
      cityAgg[key] = {{
        code: cidStr,
        name: cidStr + ' (' + ufStr + ')',
        uf: ufStr,
        mercado: mercadoStr,
        totA26: 0, totJ26: 0,
        claroA26: 0, claroJ26: 0,
        vivoA26: 0, vivoJ26: 0,
        timA26: 0, timJ26: 0,
        oiA26: 0, oiJ26: 0,
        outrosA26: 0, outrosJ26: 0,
        isps: {{}}
      }};
    }}

    const cObj = cityAgg[key];
    const grpId = r[1];
    const empId = r[2];
    const empName = D.empresa[empId];
    const m = r[11];
    const j26 = m[12], a26 = m[13];

    cObj.totJ26 += j26;
    cObj.totA26 += a26;

    const isClaro = (grpId === CLARO_GRP_ID || empName.toUpperCase().startsWith('CLARO'));
    if (isClaro) {{
      cObj.claroJ26 += j26; cObj.claroA26 += a26;
    }} else if (grpId === VIVO_GRP_ID) {{
      cObj.vivoJ26 += j26; cObj.vivoA26 += a26;
    }} else if (grpId === TIM_GRP_ID) {{
      cObj.timJ26 += j26; cObj.timA26 += a26;
    }} else if (grpId === OI_GRP_ID) {{
      cObj.oiJ26 += j26; cObj.oiA26 += a26;
    }} else {{
      cObj.outrosJ26 += j26; cObj.outrosA26 += a26;
      cObj.isps[empName] = (cObj.isps[empName] || 0) + a26;
    }}
  }}

  let html = `<thead>
    <tr>
      <th class="l" rowspan="2">Município</th>
      <th colspan="4" style="text-align:center;background:#fff5f5;color:var(--red);border-left:2px solid var(--red)">Claro</th>
      <th colspan="4" style="text-align:center;background:#faf6fd;color:#6b4b8a;border-left:2px solid #6b4b8a">Vivo</th>
      <th colspan="4" style="text-align:center;background:#f4f8fc;color:#2a5d8f;border-left:2px solid #2a5d8f">Tim</th>
      <th colspan="4" style="text-align:center;background:#fffdf5;color:#c98a15;border-left:2px solid #c98a15">Oi / Nio</th>
      <th colspan="4" style="text-align:center;background:#f9fafb;color:#7f8c8d;border-left:2px solid #7f8c8d">ISPs (Outros)</th>
      <th colspan="2" style="text-align:center;background:#edf1f5;border-left:2px solid var(--nav)">Total Mercado</th>
      <th rowspan="2" style="text-align:center;border-left:2px solid var(--line)">Posição Claro</th>
    </tr>
    <tr>
      <th style="background:#fff5f5">Base</th><th style="background:#fff5f5">Share %</th><th style="background:#fff5f5">Adds</th><th style="background:#fff5f5">Net Share</th>
      <th style="background:#faf6fd">Base</th><th style="background:#faf6fd">Share %</th><th style="background:#faf6fd">Adds</th><th style="background:#faf6fd">Net Share</th>
      <th style="background:#f4f8fc">Base</th><th style="background:#f4f8fc">Share %</th><th style="background:#f4f8fc">Adds</th><th style="background:#f4f8fc">Net Share</th>
      <th style="background:#fffdf5">Base</th><th style="background:#fffdf5">Share %</th><th style="background:#fffdf5">Adds</th><th style="background:#fffdf5">Net Share</th>
      <th style="background:#f9fafb">Base</th><th style="background:#f9fafb">Share %</th><th style="background:#f9fafb">Adds</th><th style="background:#f9fafb">Net Share</th>
      <th style="background:#edf1f5">Base</th><th style="background:#edf1f5">Adds</th>
    </tr>
  </thead><tbody>`;

  const groups = [
    {{ id: 'grandes', title: 'Grandes Mercados', items: [] }},
    {{ id: 'desenv', title: 'Mercados em Desenvolvimento', items: [] }},
    {{ id: 'demais', title: 'Demais Municípios', items: [] }}
  ];

  Object.values(cityAgg).forEach(c => {{
    if (c.totA26 === 0 && c.totJ26 === 0) return;
    if (c.mercado === 'Grandes Mercados') groups[0].items.push(c);
    else if (c.mercado === 'Mercados em Desenvolvimento') groups[1].items.push(c);
    else groups[2].items.push(c);
  }});

  // Ordena cidades alfabeticamente dentro de cada divisão
  groups.forEach(g => {{
    g.items.sort((a, b) => a.name.localeCompare(b.name));
  }});

  let totGeralA = 0, totGeralJ = 0;
  let totClaroA = 0, totClaroJ = 0;
  let totVivoA = 0, totVivoJ = 0;
  let totTimA = 0, totTimJ = 0;
  let totOiA = 0, totOiJ = 0;
  let totOutrosA = 0, totOutrosJ = 0;
  let totIsps = {{}};

  groups.forEach(g => {{
    if (!g.items.length) return;

    // Cabeçalho da Divisão
    html += `<tr style="background:#edf2f7;color:var(--nav);font-weight:700">
      <td colspan="23" style="padding:7px 12px;font-size:11.5px;letter-spacing:0.5px"><span style="display:inline-block;width:6px;height:6px;background:var(--blue);border-radius:1px;margin-right:6px"></span>${{g.title.toUpperCase()}}</td>
    </tr>`;

    let subTotA = 0, subTotJ = 0;
    let subClaroA = 0, subClaroJ = 0;
    let subVivoA = 0, subVivoJ = 0;
    let subTimA = 0, subTimJ = 0;
    let subOiA = 0, subOiJ = 0;
    let subOutrosA = 0, subOutrosJ = 0;
    let subIsps = {{}};

    g.items.forEach(d => {{
      subTotA += d.totA26; subTotJ += d.totJ26;
      subClaroA += d.claroA26; subClaroJ += d.claroJ26;
      subVivoA += d.vivoA26; subVivoJ += d.vivoJ26;
      subTimA += d.timA26; subTimJ += d.timJ26;
      subOiA += d.oiA26; subOiJ += d.oiJ26;
      subOutrosA += d.outrosA26; subOutrosJ += d.outrosJ26;
      for (const isp in d.isps) {{
        subIsps[isp] = (subIsps[isp] || 0) + d.isps[isp];
        totIsps[isp] = (totIsps[isp] || 0) + d.isps[isp];
      }}

      totGeralA += d.totA26; totGeralJ += d.totJ26;
      totClaroA += d.claroA26; totClaroJ += d.claroJ26;
      totVivoA += d.vivoA26; totVivoJ += d.vivoJ26;
      totTimA += d.timA26; totTimJ += d.timJ26;
      totOiA += d.oiA26; totOiJ += d.oiJ26;
      totOutrosA += d.outrosA26; totOutrosJ += d.outrosJ26;

      const netTot = d.totA26 - d.totJ26;
      const addClaro = d.claroA26 - d.claroJ26;
      const addVivo = d.vivoA26 - d.vivoJ26;
      const addTim = d.timA26 - d.timJ26;
      const addOi = d.oiA26 - d.oiJ26;
      const addOutros = d.outrosA26 - d.outrosJ26;

      // Net Share positivo oficial
      let posSum = 0;
      [addClaro, addVivo, addTim, addOi, addOutros].forEach(a => {{ if (a > 0) posSum += a; }});

      const shClaro = d.totA26 > 0 ? (d.claroA26 / d.totA26 * 100) : 0;
      const nsClaro = (posSum > 0 && addClaro > 0) ? (addClaro / posSum * 100) : 0;

      const shVivo = d.totA26 > 0 ? (d.vivoA26 / d.totA26 * 100) : 0;
      const nsVivo = (posSum > 0 && addVivo > 0) ? (addVivo / posSum * 100) : 0;

      const shTim = d.totA26 > 0 ? (d.timA26 / d.totA26 * 100) : 0;
      const nsTim = (posSum > 0 && addTim > 0) ? (addTim / posSum * 100) : 0;

      const shOi = d.totA26 > 0 ? (d.oiA26 / d.totA26 * 100) : 0;
      const nsOi = (posSum > 0 && addOi > 0) ? (addOi / posSum * 100) : 0;

      const shOutros = d.totA26 > 0 ? (d.outrosA26 / d.totA26 * 100) : 0;
      const nsOutros = (posSum > 0 && addOutros > 0) ? (addOutros / posSum * 100) : 0;

      // Posição Claro: avaliada contra concorrentes individuais e o maior ISP da cidade
      const maxIsp = Object.values(d.isps).length ? Math.max(...Object.values(d.isps)) : 0;
      const comps = [
        {{ p: 'CLARO', b: d.claroA26 }},
        {{ p: 'VIVO', b: d.vivoA26 }},
        {{ p: 'TIM', b: d.timA26 }},
        {{ p: 'OI', b: d.oiA26 }},
        {{ p: 'ISP', b: maxIsp }}
      ].sort((a, b) => b.b - a.b);
      const claroRank = comps.findIndex(x => x.p === 'CLARO') + 1;
      const posClass = claroRank === 1 ? 'pos-1' : (claroRank === 2 ? 'pos-2' : (claroRank === 3 ? 'pos-3' : 'pos-other'));

      html += `<tr>
        <td class="l"><b>${{d.name}}</b></td>
        
        <!-- Claro -->
        <td style="font-weight:700;color:var(--red)">${{fmt(d.claroA26)}}</td>
        <td style="font-weight:700;color:var(--red)">${{shClaro.toFixed(1).replace('.', ',')}}%</td>
        <td class="${{addClaro >= 0 ? 'pos' : 'neg'}}">${{addClaro >= 0 ? '+' : ''}}${{fmt(addClaro)}}</td>
        <td>${{nsClaro > 0 ? nsClaro.toFixed(1).replace('.', ',') + '%' : '0,0%'}}</td>

        <!-- Vivo -->
        <td>${{fmt(d.vivoA26)}}</td>
        <td>${{shVivo.toFixed(1).replace('.', ',')}}%</td>
        <td class="${{addVivo >= 0 ? 'pos' : 'neg'}}">${{addVivo >= 0 ? '+' : ''}}${{fmt(addVivo)}}</td>
        <td>${{nsVivo > 0 ? nsVivo.toFixed(1).replace('.', ',') + '%' : '0,0%'}}</td>

        <!-- Tim -->
        <td>${{fmt(d.timA26)}}</td>
        <td>${{shTim.toFixed(1).replace('.', ',')}}%</td>
        <td class="${{addTim >= 0 ? 'pos' : 'neg'}}">${{addTim >= 0 ? '+' : ''}}${{fmt(addTim)}}</td>
        <td>${{nsTim > 0 ? nsTim.toFixed(1).replace('.', ',') + '%' : '0,0%'}}</td>

        <!-- Oi / Nio -->
        <td>${{fmt(d.oiA26)}}</td>
        <td>${{shOi.toFixed(1).replace('.', ',')}}%</td>
        <td class="${{addOi >= 0 ? 'pos' : 'neg'}}">${{addOi >= 0 ? '+' : ''}}${{fmt(addOi)}}</td>
        <td>${{nsOi > 0 ? nsOi.toFixed(1).replace('.', ',') + '%' : '0,0%'}}</td>

        <!-- ISPs (Outros) -->
        <td>${{fmt(d.outrosA26)}}</td>
        <td>${{shOutros.toFixed(1).replace('.', ',')}}%</td>
        <td class="${{addOutros >= 0 ? 'pos' : 'neg'}}">${{addOutros >= 0 ? '+' : ''}}${{fmt(addOutros)}}</td>
        <td>${{nsOutros > 0 ? nsOutros.toFixed(1).replace('.', ',') + '%' : '0,0%'}}</td>

        <!-- Total Mercado -->
        <td><b>${{fmt(d.totA26)}}</b></td>
        <td class="${{netTot >= 0 ? 'pos' : 'neg'}}"><b>${{netTot >= 0 ? '+' : ''}}${{fmt(netTot)}}</b></td>

        <!-- Posição Claro -->
        <td style="text-align:center"><span class="pos-badge ${{posClass}}">${{claroRank}}º Lugar</span></td>
      </tr>`;
    }});

    // Linha de Subtotal da Divisão
    const subNetTot = subTotA - subTotJ;
    const subAddClaro = subClaroA - subClaroJ;
    const subAddVivo = subVivoA - subVivoJ;
    const subAddTim = subTimA - subTimJ;
    const subAddOi = subOiA - subOiJ;
    const subAddOutros = subOutrosA - subOutrosJ;

    let subPosSum = 0;
    [subAddClaro, subAddVivo, subAddTim, subAddOi, subAddOutros].forEach(a => {{ if (a > 0) subPosSum += a; }});

    const maxSubIsp = Object.values(subIsps).length ? Math.max(...Object.values(subIsps)) : 0;
    const subComps = [
      {{ p: 'CLARO', b: subClaroA }},
      {{ p: 'VIVO', b: subVivoA }},
      {{ p: 'TIM', b: subTimA }},
      {{ p: 'OI', b: subOiA }},
      {{ p: 'ISP', b: maxSubIsp }}
    ].sort((a, b) => b.b - a.b);
    const subClaroRank = subComps.findIndex(x => x.p === 'CLARO') + 1;
    const subPosClass = subClaroRank === 1 ? 'pos-1' : (subClaroRank === 2 ? 'pos-2' : (subClaroRank === 3 ? 'pos-3' : 'pos-other'));

    html += `<tr class="total-row" style="background:#f4f6fa;font-weight:700;border-bottom:2px solid var(--line)">
      <td class="l"><b>SUBTOTAL — ${{g.title.toUpperCase()}}</b></td>
      
      <!-- Claro -->
      <td style="color:var(--red)">${{fmt(subClaroA)}}</td>
      <td style="color:var(--red)">${{subTotA > 0 ? (subClaroA / subTotA * 100).toFixed(1).replace('.', ',') + '%' : '0,0%'}}</td>
      <td class="${{subAddClaro >= 0 ? 'pos' : 'neg'}}">${{subAddClaro >= 0 ? '+' : ''}}${{fmt(subAddClaro)}}</td>
      <td>${{subPosSum > 0 && subAddClaro > 0 ? (subAddClaro / subPosSum * 100).toFixed(1).replace('.', ',') + '%' : '0,0%'}}</td>

      <!-- Vivo -->
      <td>${{fmt(subVivoA)}}</td>
      <td>${{subTotA > 0 ? (subVivoA / subTotA * 100).toFixed(1).replace('.', ',') + '%' : '0,0%'}}</td>
      <td class="${{subAddVivo >= 0 ? 'pos' : 'neg'}}">${{subAddVivo >= 0 ? '+' : ''}}${{fmt(subAddVivo)}}</td>
      <td>${{subPosSum > 0 && subAddVivo > 0 ? (subAddVivo / subPosSum * 100).toFixed(1).replace('.', ',') + '%' : '0,0%'}}</td>

      <!-- Tim -->
      <td>${{fmt(subTimA)}}</td>
      <td>${{subTotA > 0 ? (subTimA / subTotA * 100).toFixed(1).replace('.', ',') + '%' : '0,0%'}}</td>
      <td class="${{subAddTim >= 0 ? 'pos' : 'neg'}}">${{subAddTim >= 0 ? '+' : ''}}${{fmt(subAddTim)}}</td>
      <td>${{subPosSum > 0 && subAddTim > 0 ? (subAddTim / subPosSum * 100).toFixed(1).replace('.', ',') + '%' : '0,0%'}}</td>

      <!-- Oi / Nio -->
      <td>${{fmt(subOiA)}}</td>
      <td>${{subTotA > 0 ? (subOiA / subTotA * 100).toFixed(1).replace('.', ',') + '%' : '0,0%'}}</td>
      <td class="${{subAddOi >= 0 ? 'pos' : 'neg'}}">${{subAddOi >= 0 ? '+' : ''}}${{fmt(subAddOi)}}</td>
      <td>${{subPosSum > 0 && subAddOi > 0 ? (subAddOi / subPosSum * 100).toFixed(1).replace('.', ',') + '%' : '0,0%'}}</td>

      <!-- ISPs -->
      <td>${{fmt(subOutrosA)}}</td>
      <td>${{subTotA > 0 ? (subOutrosA / subTotA * 100).toFixed(1).replace('.', ',') + '%' : '0,0%'}}</td>
      <td class="${{subAddOutros >= 0 ? 'pos' : 'neg'}}">${{subAddOutros >= 0 ? '+' : ''}}${{fmt(subAddOutros)}}</td>
      <td>${{subPosSum > 0 && subAddOutros > 0 ? (subAddOutros / subPosSum * 100).toFixed(1).replace('.', ',') + '%' : '0,0%'}}</td>

      <!-- Total Mercado -->
      <td><b>${{fmt(subTotA)}}</b></td>
      <td class="${{subNetTot >= 0 ? 'pos' : 'neg'}}"><b>${{subNetTot >= 0 ? '+' : ''}}${{fmt(subNetTot)}}</b></td>

      <!-- Posição Claro -->
      <td style="text-align:center"><span class="pos-badge ${{subPosClass}}">${{subClaroRank}}º Lugar</span></td>
    </tr>`;
  }});

  // LINHA TOTAL GERAL DE TODAS AS CIDADES
  if (totGeralA > 0) {{
    const netGeralTot = totGeralA - totGeralJ;
    const addClaroGeral = totClaroA - totClaroJ;
    const addVivoGeral = totVivoA - totVivoJ;
    const addTimGeral = totTimA - totTimJ;
    const addOiGeral = totOiA - totOiJ;
    const addOutrosGeral = totOutrosA - totOutrosJ;

    let totPosSum = 0;
    [addClaroGeral, addVivoGeral, addTimGeral, addOiGeral, addOutrosGeral].forEach(a => {{ if (a > 0) totPosSum += a; }});

    const maxTotIsp = Object.values(totIsps).length ? Math.max(...Object.values(totIsps)) : 0;
    const totComps = [
      {{ p: 'CLARO', b: totClaroA }},
      {{ p: 'VIVO', b: totVivoA }},
      {{ p: 'TIM', b: totTimA }},
      {{ p: 'OI', b: totOiA }},
      {{ p: 'ISP', b: maxTotIsp }}
    ].sort((a, b) => b.b - a.b);
    const claroRankGeral = totComps.findIndex(x => x.p === 'CLARO') + 1;
    const posClassGeral = claroRankGeral === 1 ? 'pos-1' : (claroRankGeral === 2 ? 'pos-2' : (claroRankGeral === 3 ? 'pos-3' : 'pos-other'));

    html += `<tr class="total-row" style="background:#e8edf3;font-weight:800;border-top:3px solid var(--nav)">
      <td class="l"><b>TOTAL GERAL DO CENÁRIO</b></td>
      
      <!-- Claro -->
      <td style="color:var(--red)">${{fmt(totClaroA)}}</td>
      <td style="color:var(--red)">${{(totClaroA / totGeralA * 100).toFixed(1).replace('.', ',')}}%</td>
      <td class="${{addClaroGeral >= 0 ? 'pos' : 'neg'}}">${{addClaroGeral >= 0 ? '+' : ''}}${{fmt(addClaroGeral)}}</td>
      <td>${{totPosSum > 0 && addClaroGeral > 0 ? (addClaroGeral / totPosSum * 100).toFixed(1).replace('.', ',') + '%' : '0,0%'}}</td>

      <!-- Vivo -->
      <td>${{fmt(totVivoA)}}</td>
      <td>${{(totVivoA / totGeralA * 100).toFixed(1).replace('.', ',')}}%</td>
      <td class="${{addVivoGeral >= 0 ? 'pos' : 'neg'}}">${{addVivoGeral >= 0 ? '+' : ''}}${{fmt(addVivoGeral)}}</td>
      <td>${{totPosSum > 0 && addVivoGeral > 0 ? (addVivoGeral / totPosSum * 100).toFixed(1).replace('.', ',') + '%' : '0,0%'}}</td>

      <!-- Tim -->
      <td>${{fmt(totTimA)}}</td>
      <td>${{(totTimA / totGeralA * 100).toFixed(1).replace('.', ',')}}%</td>
      <td class="${{addTimGeral >= 0 ? 'pos' : 'neg'}}">${{addTimGeral >= 0 ? '+' : ''}}${{fmt(addTimGeral)}}</td>
      <td>${{totPosSum > 0 && addTimGeral > 0 ? (addTimGeral / totPosSum * 100).toFixed(1).replace('.', ',') + '%' : '0,0%'}}</td>

      <!-- Oi / Nio -->
      <td>${{fmt(totOiA)}}</td>
      <td>${{(totOiA / totGeralA * 100).toFixed(1).replace('.', ',')}}%</td>
      <td class="${{addOiGeral >= 0 ? 'pos' : 'neg'}}">${{addOiGeral >= 0 ? '+' : ''}}${{fmt(addOiGeral)}}</td>
      <td>${{totPosSum > 0 && addOiGeral > 0 ? (addOiGeral / totPosSum * 100).toFixed(1).replace('.', ',') + '%' : '0,0%'}}</td>

      <!-- ISPs -->
      <td>${{fmt(totOutrosA)}}</td>
      <td>${{(totOutrosA / totGeralA * 100).toFixed(1).replace('.', ',')}}%</td>
      <td class="${{addOutrosGeral >= 0 ? 'pos' : 'neg'}}">${{addOutrosGeral >= 0 ? '+' : ''}}${{fmt(addOutrosGeral)}}</td>
      <td>${{totPosSum > 0 && addOutrosGeral > 0 ? (addOutrosGeral / totPosSum * 100).toFixed(1).replace('.', ',') + '%' : '0,0%'}}</td>

      <!-- Total Mercado -->
      <td><b>${{fmt(totGeralA)}}</b></td>
      <td class="${{netGeralTot >= 0 ? 'pos' : 'neg'}}"><b>${{netGeralTot >= 0 ? '+' : ''}}${{fmt(netGeralTot)}}</b></td>

      <!-- Posição Claro -->
      <td style="text-align:center"><span class="pos-badge ${{posClassGeral}}">${{claroRankGeral}}º Lugar</span></td>
    </tr>`;
  }}

  html += '</tbody>';
  tEl.innerHTML = html;
}}

/* ============ VISÃO 4: DETALHADA HISTÓRICA & PROJEÇÃO DE ULTRAPASSAGEM ============ */
function renderDetalhada(fRows) {{
  // 1. Renderiza Bloco de Projeção de Ultrapassagem
  renderProjecao(fRows);

  // 2. Renderiza Matriz Histórica (14 meses) com as 4 linhas por operadora
  renderMatrizDetalhada(fRows);

  // 3. Renderiza Tabela de Registros Analíticos
  renderAnalytic(fRows);
}}

function renderProjecao(fRows) {{
  let claroA26 = 0, claroJ26 = 0;
  let playersA26 = {{}}, playersJ26 = {{}};
  let ispsA26 = {{}}, ispsJ26 = {{}};

  for (let i = 0; i < fRows.length; i++) {{
    const r = fRows[i];
    const grpName = D.grupo[r[1]];
    const empName = D.empresa[r[2]];
    const m = r[11];
    const j26 = m[12], a26 = m[13];

    const isClaro = (r[1] === CLARO_GRP_ID || empName.toUpperCase().startsWith('CLARO'));
    let pKey = 'Outros';
    if (isClaro) pKey = 'Claro';
    else if (r[1] === VIVO_GRP_ID) pKey = 'Vivo';
    else if (r[1] === TIM_GRP_ID) pKey = 'Tim';
    else if (r[1] === OI_GRP_ID) pKey = 'Oi';
    else {{
      ispsA26[empName] = (ispsA26[empName] || 0) + a26;
      ispsJ26[empName] = (ispsJ26[empName] || 0) + j26;
    }}

    playersA26[pKey] = (playersA26[pKey] || 0) + a26;
    playersJ26[pKey] = (playersJ26[pKey] || 0) + j26;

    if (isClaro) {{
      claroA26 += a26;
      claroJ26 += j26;
    }}
  }}

  // Concorrentes diretos institucionais (telcos nacionais)
  const TELCOS = ['Claro', 'Vivo', 'Oi', 'Tim'];
  const sortedTelcos = TELCOS.map(t => ({{ p: t, base: playersA26[t] || 0, net: (playersA26[t] || 0) - (playersJ26[t] || 0) }}))
                             .sort((a, b) => b.base - a.base);
  const claroRankTelco = sortedTelcos.findIndex(x => x.p === 'Claro') + 1;
  const secondTelco = (sortedTelcos.find(x => x.p !== 'Claro') || {{ p: 'Oi', base: 0, net: 0 }});
  const isLeader = claroA26 > 0 && claroRankTelco === 1 && claroA26 > secondTelco.base;
  const telcoAdvantage = claroA26 - secondTelco.base;

  // Maior ISP individual
  let maxIspName = 'Você Telecom', maxIspBase = 0, maxIspNet = 0;
  for (const isp in ispsA26) {{
    if (ispsA26[isp] > maxIspBase) {{
      maxIspBase = ispsA26[isp];
      maxIspName = isp;
      maxIspNet = ispsA26[isp] - (ispsJ26[isp] || 0);
    }}
  }}

  const bEl = document.getElementById('boxProjecao');

  // Caso especial: Sem rede cabeada / Base zero (ex: DDD 93)
  let totAgo26 = 0;
  for (const p in playersA26) {{ totAgo26 += playersA26[p]; }}

  if (totAgo26 === 0 || claroA26 === 0) {{
    bEl.innerHTML = `
      <div class="proj-card" style="background:#f8fafc; border-color:#cbd5e1">
        <div class="lbl" style="color:#64748b">Posição Oficial de Mercado</div>
        <div class="val" style="color:#475569">Sem Rede Cabeada (Base 0)</div>
        <div class="desc" style="color:#64748b">
          A Claro não possui rede cabeada (GPON/HFC) ativa no DDD/recorte selecionado (0 clientes).
        </div>
      </div>
      <div class="proj-card">
        <div class="lbl">Concorrentes no Recorte</div>
        <div class="val" style="color:var(--ink2)">${{totAgo26 > 0 ? (sortedTelcos[0]?.p + ': ' + fmt(sortedTelcos[0]?.base)) : 'Sem Acessos Cabeados'}}</div>
        <div class="desc">${{totAgo26 > 0 ? 'Concorrente com maior presença no recorte selecionado.' : 'Nenhuma operadora nacional possui base cabeada ativa com os filtros selecionados.'}}</div>
      </div>
      <div class="proj-card">
        <div class="lbl">Maior Provedor Individual (ISP)</div>
        <div class="val" style="color:var(--blue)">${{maxIspBase > 0 ? maxIspName : '—'}}</div>
        <div class="desc">${{maxIspBase > 0 ? ('Base: ' + fmt(maxIspBase) + ' acessos') : 'Sem provedores registrados no recorte'}}</div>
      </div>
      <div class="proj-card">
        <div class="lbl">Horizonte de Blindagem / Liderança</div>
        <div class="val" style="color:var(--ink3)">Não Aplicável</div>
        <div class="desc">Mercado sem presença de rede cabeada Claro ativa.</div>
      </div>
      <div class="proj-card">
        <div class="lbl">Diretriz Estratégica</div>
        <div class="val" style="font-size:16px;color:var(--amber)">Expansão de Rede</div>
        <div class="desc">Necessária expansão de infraestrutura para início de comercialização residencial.</div>
      </div>
      <div class="proj-card" style="grid-column: 1 / -1; background:#fbfcfe">
        <div class="lbl">Nota Metodológica de Liderança Corporativa</div>
        <div class="desc" style="font-size:12px;line-height:1.6;color:var(--ink2);margin-top:4px">
          No DDD ou recorte selecionado, a Claro não possui rede física cabeada (GPON/HFC) instalada, registrando 0 clientes. 
          Portanto, não é aplicável métrica de liderança ou dominância de mercado para serviços cabeados nesta localidade.
        </div>
      </div>
    `;
    return;
  }}

  // Dinâmica de Adições Líquidas
  const netClaro = claroA26 - claroJ26;
  const netSecond = secondTelco.net;
  const netDiff = netSecond - netClaro; // aproximação da 2ª colocada

  // Projeção temporal: meses até aproximação caso a 2ª colocada cresça mais rápido
  let mesesAproximacao = '—';
  if (isLeader) {{
    if (netDiff > 0 && telcoAdvantage > 0) {{
      const m = Math.round(telcoAdvantage / netDiff);
      mesesAproximacao = `${{m}} meses`;
    }} else {{
      mesesAproximacao = 'Estável / Ampliando';
    }}
  }}

  // Metas de adições líquidas da Claro para blindagem da liderança
  const targetNet12m = Math.max(0, netSecond + Math.round(telcoAdvantage / 24));
  const targetNet24m = Math.max(0, netSecond + Math.round(telcoAdvantage / 36));

  bEl.innerHTML = `
    <div class="proj-card" style="background:#eaf6ec; border-color:#b8e2c4">
      <div class="lbl" style="color:#1e6b37">Posição Oficial de Mercado</div>
      <div class="val" style="color:#1e6b37">${{isLeader ? '1º Lugar (Líder Absoluta)' : claroRankTelco + 'º Lugar'}}</div>
      <div class="desc" style="color:#2e7d32">
        A Claro lidera com <b>${{fmt(claroA26)}}</b> clientes (${{telcoAdvantage >= 0 ? '+' : ''}}${{fmt(telcoAdvantage)}} sobre a 2ª colocada, ${{secondTelco.p}}).
      </div>
    </div>

    <div class="proj-card">
      <div class="lbl">2ª Colocada Concorrente Directa</div>
      <div class="val" style="color:#6b4b8a">${{secondTelco.p}}: ${{fmt(secondTelco.base)}}</div>
      <div class="desc">Adds Mês: ${{secondTelco.net >= 0 ? '+' : ''}}${{fmt(secondTelco.net)}} · Margem Claro: <b>+${{fmt(telcoAdvantage)}}</b> acessos</div>
    </div>

    <div class="proj-card">
      <div class="lbl">Maior Provedor Individual (ISP)</div>
      <div class="val" style="color:var(--blue)">${{maxIspName}}</div>
      <div class="desc">Base: <b>${{fmt(maxIspBase)}}</b> (${{maxIspNet >= 0 ? '+' : ''}}${{fmt(maxIspNet)}} adds) · Claro tem <b>+${{fmt(claroA26 - maxIspBase)}}</b> acessos a mais</div>
    </div>

    <div class="proj-card">
      <div class="lbl">Horizonte de Blindagem da Liderança</div>
      <div class="val" style="color:var(--amber)">${{mesesAproximacao}}</div>
      <div class="desc">Ritmo atual: Claro ${{netClaro >= 0 ? '+' : ''}}${{fmt(netClaro)}} vs. ${{secondTelco.p}} ${{netSecond >= 0 ? '+' : ''}}${{fmt(netSecond)}}/mês</div>
    </div>

    <div class="proj-card">
      <div class="lbl">Meta de Adds Claro (12m / 24m)</div>
      <div class="val" style="font-size:16px">+${{fmt(targetNet12m)}} <span style="font-size:11px;color:var(--ink3)">(12m)</span> · +${{fmt(targetNet24m)}} <span style="font-size:11px;color:var(--ink3)">(24m)</span></div>
      <div class="desc">Adições mensais recomendadas para sustentar a margem de liderança</div>
    </div>

    <div class="proj-card" style="grid-column: 1 / -1; background:#fbfcfe">
      <div class="lbl">Nota Metodológica de Liderança Corporativa</div>
      <div class="desc" style="font-size:12px;line-height:1.6;color:var(--ink2);margin-top:4px">
        O cluster <b>Outros</b> agrega centenas de provedores independentes (sendo a maior empresa individual <b>${{maxIspName}}</b> com ${{fmt(maxIspBase)}} clientes). 
        <b>No confronto direto entre operadoras consolidadas, a Claro é Líder Absoluta na Regional Norte</b> com ${{fmt(claroA26)}} acessos ativos, à frente de Oi (${{fmt(playersA26['Oi'] || 0)}}), Vivo (${{fmt(playersA26['Vivo'] || 0)}}) e Tim (${{fmt(playersA26['Tim'] || 0)}}).
      </div>
    </div>
  `;
}}

// Função para desenhar o gráfico SVG de evolução da base (14 meses)
function renderHistoryLineChart(aggData) {{
  const wrap = document.getElementById('lineChartSvgWrap');
  const leg = document.getElementById('lineChartLegend');
  if (!wrap || !leg) return;

  const PLAYERS_CHART = [
    {{ id: 'Claro', name: 'Claro', color: '#c0392b', strokeWidth: 2.8 }},
    {{ id: 'Vivo', name: 'Vivo', color: '#6b4b8a', strokeWidth: 2.2 }},
    {{ id: 'Tim', name: 'Tim', color: '#2a5d8f', strokeWidth: 2.2 }},
    {{ id: 'Oi', name: 'Oi / Nio', color: '#c98a15', strokeWidth: 2.2 }},
    {{ id: 'Outros', name: 'Outros (ISPs)', color: '#7f8c8d', strokeWidth: 2.2 }}
  ];

  // Legenda com valores atuais
  leg.innerHTML = PLAYERS_CHART.map(p => `
    <div class="chart-leg-item">
      <span class="chart-leg-dot" style="background:${{p.color}}"></span>
      <span>${{p.name}}:</span>
      <b style="color:${{p.color}}">${{fmt(aggData[p.id]?.base[13] || 0)}}</b>
    </div>
  `).join('') + `
    <div class="chart-leg-item" style="margin-left:auto;font-size:11px;color:var(--ink3)">
      <span>Total Mercado ago/26: <b>${{fmt(aggData['Total Geral']?.base[13] || 0)}}</b></span>
    </div>
  `;

  // Dimensões do SVG
  const W = 960, H = 250;
  const padL = 75, padR = 25, padT = 20, padB = 35;
  const plotW = W - padL - padR;
  const plotH = H - padT - padB;

  // Encontrar valor máximo
  let maxVal = 0;
  PLAYERS_CHART.forEach(p => {{
    const arr = aggData[p.id]?.base || [];
    arr.forEach(v => {{ if (v > maxVal) maxVal = v; }});
  }});
  maxVal = Math.ceil(maxVal * 1.12 / 100000) * 100000;
  if (maxVal <= 0) maxVal = 1000000;

  // Grid e Eixos Y
  let svg = `<svg viewBox="0 0 ${{W}} ${{H}}" style="width:100%;height:auto;display:block;font-family:'Segoe UI',sans-serif">`;
  const yTicks = 5;
  for (let i = 0; i <= yTicks; i++) {{
    const val = (maxVal / yTicks) * i;
    const y = padT + plotH - (val / maxVal * plotH);
    svg += `<line x1="${{padL}}" y1="${{y}}" x2="${{W - padR}}" y2="${{y}}" stroke="#eef1f4" stroke-dasharray="${{i === 0 ? 'none' : '3,3'}}" stroke-width="1"/>`;
    svg += `<text x="${{padL - 8}}" y="${{y + 4}}" font-size="10" fill="#718096" text-anchor="end">${{fmt(val)}}</text>`;
  }}

  // Eixo X (Meses)
  const nMonths = MONTHS.length;
  const stepX = plotW / (nMonths - 1);
  MONTHS.forEach((m, idx) => {{
    const x = padL + idx * stepX;
    const isCur = idx === 13;
    svg += `<line x1="${{x}}" y1="${{padT + plotH}}" x2="${{x}}" y2="${{padT + plotH + 5}}" stroke="#cbd5e0" stroke-width="1"/>`;
    svg += `<text x="${{x}}" y="${{padT + plotH + 18}}" font-size="10.5" font-weight="${{isCur ? '700' : '500'}}" fill="${{isCur ? '#c0392b' : '#4a5568'}}" text-anchor="middle">${{m}}</text>`;
    if (isCur) {{
      svg += `<rect x="${{x - 18}}" y="${{padT}}" width="36" height="${{plotH}}" fill="rgba(224,32,32,0.03)" pointer-events="none"/>`;
    }}
  }});

  // Linhas por Operadora
  PLAYERS_CHART.forEach(p => {{
    const arr = aggData[p.id]?.base || [];
    if (!arr.length) return;

    let pts = [];
    arr.forEach((v, idx) => {{
      const x = padL + idx * stepX;
      const y = padT + plotH - (v / maxVal * plotH);
      pts.push(`${{x.toFixed(1)}},${{y.toFixed(1)}}`);
    }});

    // Linha
    svg += `<polyline fill="none" stroke="${{p.color}}" stroke-width="${{p.strokeWidth}}" stroke-linejoin="round" stroke-linecap="round" points="${{pts.join(' ')}}"/>`;

    // Círculos nos pontos com title tooltip
    arr.forEach((v, idx) => {{
      const x = padL + idx * stepX;
      const y = padT + plotH - (v / maxVal * plotH);
      const isCur = idx === 13;
      svg += `<circle cx="${{x.toFixed(1)}}" cy="${{y.toFixed(1)}}" r="${{isCur ? '4.5' : '3'}}" fill="#ffffff" stroke="${{p.color}}" stroke-width="2">
        <title>${{p.name}} — ${{MONTHS[idx]}}: ${{fmt(v)}} clientes</title>
      </circle>`;
    }});
  }});

  svg += `</svg>`;
  wrap.innerHTML = svg;
}}

function renderMatrizDetalhada(fRows) {{
  const tEl = document.getElementById('tblDetalhadaHistorica');
  const OPERATORS = ['Total Geral', 'Claro', 'Vivo', 'Tim', 'Oi', 'SKY/WERTHEIN', 'Outros'];

  const aggData = {{}};
  OPERATORS.forEach(op => {{
    aggData[op] = {{
      base: new Array(14).fill(0),
      ddds: {{}}
    }};
    for (let d = 91; d <= 99; d++) {{
      aggData[op].ddds[String(d)] = new Array(14).fill(0);
    }}
  }});

  for (let i = 0; i < fRows.length; i++) {{
    const r = fRows[i];
    const grpName = D.grupo[r[1]];
    const empName = D.empresa[r[2]];
    const dddStr = D.ddd[r[3]];
    const m = r[11];

    let opKey = 'Outros';
    if (r[1] === CLARO_GRP_ID || empName.toUpperCase().startsWith('CLARO')) opKey = 'Claro';
    else if (r[1] === VIVO_GRP_ID) opKey = 'Vivo';
    else if (r[1] === TIM_GRP_ID) opKey = 'Tim';
    else if (r[1] === OI_GRP_ID) opKey = 'Oi';
    else if (grpName.toUpperCase().includes('SKY') || grpName.toUpperCase().includes('WERTHEIN')) opKey = 'SKY/WERTHEIN';

    for (let k = 0; k < 14; k++) {{
      const val = m[k];
      aggData['Total Geral'].base[k] += val;
      if (aggData['Total Geral'].ddds[dddStr]) aggData['Total Geral'].ddds[dddStr][k] += val;

      aggData[opKey].base[k] += val;
      if (aggData[opKey].ddds[dddStr]) aggData[opKey].ddds[dddStr][k] += val;
    }}
  }}

  // Renderiza Gráfico Histórico no Topo da Visão Detalhada
  renderHistoryLineChart(aggData);

  // Cabeçalho da Matriz com destaque no Mês Atual (ago/26)
  let html = '<thead><tr><th class="l">Operadora & Dimensão Analítica</th>';
  MONTHS.forEach((m, idx) => {{
    const isCur = idx === 13;
    html += `<th class="${{isCur ? 'col-cur-mth-hdr' : ''}}">${{m}}${{isCur ? ' <span style="font-size:9px;background:var(--red);color:#fff;padding:1px 4px;border-radius:2px;margin-left:2px">Atual</span>' : ''}}</th>`;
  }});
  html += '<th>MoM</th><th>YoY</th></tr></thead><tbody>';

  // Determina lista de DDDs ativos conforme os filtros
  let activeDdds = [];
  if (sel.ddd && sel.ddd.size > 0) {{
    activeDdds = [...sel.ddd].map(id => D.ddd[id]).sort();
  }} else {{
    const presentDdds = new Set();
    fRows.forEach(r => presentDdds.add(D.ddd[r[3]]));
    activeDdds = ['91', '92', '93', '94', '95', '96', '97', '98', '99'].filter(d => presentDdds.has(d));
    if (activeDdds.length === 0) activeDdds = ['91', '92', '93', '94', '95', '96', '97', '98', '99'];
  }}

  OPERATORS.forEach(op => {{
    const d = aggData[op];
    const isClaro = op === 'Claro';
    const isVivo = op === 'Vivo';
    const isTim = op === 'Tim';
    const isOi = op === 'Oi';
    const isSky = op === 'SKY/WERTHEIN';
    const isTot = op === 'Total Geral';
    const opClean = op.replace('/', '_').replace(' ', '_');

    let opRowClass = 'outros-row';
    if (isClaro) opRowClass = 'claro-row';
    else if (isVivo) opRowClass = 'vivo-row';
    else if (isTim) opRowClass = 'tim-row';
    else if (isOi) opRowClass = 'oi-row';
    else if (isSky) opRowClass = 'sky-row';
    else if (isTot) opRowClass = 'isp-tot-row';

    const kBase = `${{opClean}}_base`;
    const kShare = `${{opClean}}_share`;
    const kAdds = `${{opClean}}_adds`;
    const kNetShare = `${{opClean}}_netshare`;
    const dddCountNote = `<span style="font-size:10px;color:var(--ink3);font-weight:400">(${{activeDdds.length}} DDD${{activeDdds.length > 1 ? 's' : ''}})</span>`;

    // 1. Linha Mestre: Base de Acessos
    html += `<tr class="${{opRowClass}}" style="cursor:pointer" onclick="toggleDetIndicator('${{kBase}}')">
      <td class="l"><b><span id="ico_${{kBase}}">▸</span> ${{op}} — Base de Acessos</b> ${{dddCountNote}}</td>`;
    d.base.forEach((v, idx) => {{
      html += `<td class="${{idx === 13 ? 'col-cur-mth' : ''}}">${{fmt(v)}}</td>`;
    }});
    html += `<td>${{pct(d.base[13] - d.base[12], d.base[12])}}</td><td>${{pct(d.base[13] - d.base[1], d.base[1])}}</td></tr>`;

    // 1.1 Abertura de DDDs da Base de Acessos
    activeDdds.forEach(dddStr => {{
      const bDdd = d.ddds[dddStr] || new Array(14).fill(0);
      html += `<tr class="det-sub-${{kBase}}" style="display:none;background:#f8fafc;color:var(--ink)">
        <td class="l" style="padding-left:34px;font-weight:600">↳ DDD ${{dddStr}} · Base</td>`;
      bDdd.forEach((v, idx) => {{
        html += `<td class="${{idx === 13 ? 'col-cur-mth' : ''}}">${{fmt(v)}}</td>`;
      }});
      html += `<td>${{pct(bDdd[13] - bDdd[12], bDdd[12])}}</td><td>${{pct(bDdd[13] - bDdd[1], bDdd[1])}}</td></tr>`;
    }});

    // 2. Linha Mestre: Market Share (%)
    html += `<tr style="background:#fafbfc;color:var(--ink2);cursor:pointer" onclick="toggleDetIndicator('${{kShare}}')">
      <td class="l" style="padding-left:18px"><b><span id="ico_${{kShare}}">▸</span> ${{op}} — Market Share (%)</b> ${{dddCountNote}}</td>`;
    for (let k = 0; k < 14; k++) {{
      const totK = aggData['Total Geral'].base[k];
      const s = totK > 0 ? (d.base[k] / totK * 100) : 0;
      html += `<td class="${{k === 13 ? 'col-cur-mth' : ''}}">${{s.toFixed(2).replace('.', ',')}}%</td>`;
    }}
    const s13 = aggData['Total Geral'].base[13] > 0 ? (d.base[13] / aggData['Total Geral'].base[13] * 100) : 0;
    const s12 = aggData['Total Geral'].base[12] > 0 ? (d.base[12] / aggData['Total Geral'].base[12] * 100) : 0;
    const s1 = aggData['Total Geral'].base[1] > 0 ? (d.base[1] / aggData['Total Geral'].base[1] * 100) : 0;
    html += `<td>${{pp(s13 - s12)}}</td><td>${{pp(s13 - s1)}}</td></tr>`;

    // 2.1 Abertura de DDDs do Market Share (%)
    activeDdds.forEach(dddStr => {{
      const bDdd = d.ddds[dddStr] || new Array(14).fill(0);
      const totDdd = aggData['Total Geral'].ddds[dddStr] || new Array(14).fill(0);
      html += `<tr class="det-sub-${{kShare}}" style="display:none;background:#fbfcfe;color:var(--ink2)">
        <td class="l" style="padding-left:34px;font-size:11px">↳ DDD ${{dddStr}} · Share %</td>`;
      for (let k = 0; k < 14; k++) {{
        const tk = totDdd[k];
        const s = tk > 0 ? (bDdd[k] / tk * 100) : 0;
        html += `<td class="${{k === 13 ? 'col-cur-mth' : ''}}" style="font-size:11px">${{s > 0 ? s.toFixed(1).replace('.', ',') + '%' : '0,0%'}}</td>`;
      }}
      const shDdd13 = totDdd[13] > 0 ? (bDdd[13] / totDdd[13] * 100) : 0;
      const shDdd12 = totDdd[12] > 0 ? (bDdd[12] / totDdd[12] * 100) : 0;
      const shDdd1 = totDdd[1] > 0 ? (bDdd[1] / totDdd[1] * 100) : 0;
      html += `<td style="font-size:11px">${{pp(shDdd13 - shDdd12)}}</td><td style="font-size:11px">${{pp(shDdd13 - shDdd1)}}</td></tr>`;
    }});

    // 3. Linha Mestre: Net Adds
    html += `<tr style="background:#fafbfc;color:var(--ink2);cursor:pointer" onclick="toggleDetIndicator('${{kAdds}}')">
      <td class="l" style="padding-left:18px"><b><span id="ico_${{kAdds}}">▸</span> ${{op}} — Net Adds</b> ${{dddCountNote}}</td>`;
    html += `<td>—</td>`;
    for (let k = 1; k < 14; k++) {{
      const net = d.base[k] - d.base[k-1];
      html += `<td class="${{k === 13 ? 'col-cur-mth ' : ''}}${{net >= 0 ? 'pos' : 'neg'}}">${{net >= 0 ? '+' : ''}}${{fmt(net)}}</td>`;
    }}
    const net13 = d.base[13] - d.base[12];
    const net12 = d.base[12] - d.base[11];
    const net1 = d.base[1] - d.base[0];
    html += `<td>${{net13 - net12 >= 0 ? '+' : ''}}${{fmt(net13 - net12)}}</td><td>${{net13 - net1 >= 0 ? '+' : ''}}${{fmt(net13 - net1)}}</td></tr>`;

    // 3.1 Abertura de DDDs de Net Adds
    activeDdds.forEach(dddStr => {{
      const bDdd = d.ddds[dddStr] || new Array(14).fill(0);
      html += `<tr class="det-sub-${{kAdds}}" style="display:none;background:#fbfcfe;color:var(--ink2)">
        <td class="l" style="padding-left:34px;font-size:11px">↳ DDD ${{dddStr}} · Net Adds</td>`;
      html += `<td style="font-size:11px">—</td>`;
      for (let k = 1; k < 14; k++) {{
        const netD = bDdd[k] - bDdd[k-1];
        html += `<td class="${{k === 13 ? 'col-cur-mth ' : ''}}${{netD >= 0 ? 'pos' : 'neg'}}" style="font-size:11px">${{netD >= 0 ? '+' : ''}}${{fmt(netD)}}</td>`;
      }}
      const netD13 = bDdd[13] - bDdd[12];
      const netD12 = bDdd[12] - bDdd[11];
      const netD1 = bDdd[1] - bDdd[0];
      html += `<td style="font-size:11px">${{netD13 - netD12 >= 0 ? '+' : ''}}${{fmt(netD13 - netD12)}}</td><td style="font-size:11px">${{netD13 - netD1 >= 0 ? '+' : ''}}${{fmt(netD13 - netD1)}}</td></tr>`;
    }});

    // 4. Linha Mestre: Net Share (%)
    html += `<tr style="background:#fafbfc;color:var(--ink2);border-bottom:2px solid var(--line2);cursor:pointer" onclick="toggleDetIndicator('${{kNetShare}}')">
      <td class="l" style="padding-left:18px"><b><span id="ico_${{kNetShare}}">▸</span> ${{op}} — Net Share (%)</b> ${{dddCountNote}}</td>`;
    html += `<td>—</td>`;
    for (let k = 1; k < 14; k++) {{
      const netK = d.base[k] - d.base[k-1];
      let posNetMonth = 0;
      OPERATORS.forEach(op2 => {{
        if (op2 !== 'Total Geral') {{
          const n2 = aggData[op2].base[k] - aggData[op2].base[k-1];
          if (n2 > 0) posNetMonth += n2;
        }}
      }});
      const ns = (posNetMonth > 0 && netK > 0) ? (netK / posNetMonth * 100) : 0;
      html += `<td class="${{k === 13 ? 'col-cur-mth' : ''}}">${{ns > 0 ? ns.toFixed(1).replace('.', ',') + '%' : '0,0%'}}</td>`;
    }}
    html += `<td>—</td><td>—</td></tr>`;

    // 4.1 Abertura de DDDs de Net Share (%)
    activeDdds.forEach(dddStr => {{
      const bDdd = d.ddds[dddStr] || new Array(14).fill(0);
      const totDdd = aggData['Total Geral'].ddds[dddStr] || new Array(14).fill(0);
      html += `<tr class="det-sub-${{kNetShare}}" style="display:none;background:#fbfcfe;color:var(--ink2);border-bottom:1px dashed var(--line2)">
        <td class="l" style="padding-left:34px;font-size:11px">↳ DDD ${{dddStr}} · Net Share %</td>`;
      html += `<td style="font-size:11px">—</td>`;
      for (let k = 1; k < 14; k++) {{
        const netD = bDdd[k] - bDdd[k-1];
        let posNetD = 0;
        OPERATORS.forEach(op2 => {{
          if (op2 !== 'Total Geral') {{
            const b2 = aggData[op2].ddds[dddStr] || [];
            const n2 = (b2[k] || 0) - (b2[k-1] || 0);
            if (n2 > 0) posNetD += n2;
          }}
        }});
        const ns = posNetD > 0 && netD > 0 ? (netD / posNetD * 100) : (netD > 0 ? 100 : 0);
        html += `<td class="${{k === 13 ? 'col-cur-mth' : ''}}" style="font-size:11px">${{ns > 0 ? ns.toFixed(1).replace('.', ',') + '%' : '—'}}</td>`;
      }}
      html += `<td style="font-size:11px">—</td><td style="font-size:11px">—</td></tr>`;
    }});
  }});

  html += '</tbody>';
  tEl.innerHTML = html;

  // Evento do botão de toggle todos os DDDs
  const btnTgl = document.getElementById('btnToggleAllDdd');
  if (btnTgl) {{
    btnTgl.onclick = () => {{
      const allSub = document.querySelectorAll('tr[class*="det-sub-"]');
      const anyHidden = [...allSub].some(r => r.style.display === 'none');
      allSub.forEach(r => {{ r.style.display = anyHidden ? '' : 'none'; }});
      document.querySelectorAll('span[id^="ico_"]').forEach(ico => {{
        ico.textContent = anyHidden ? '▾' : '▸';
      }});
      btnTgl.textContent = anyHidden ? 'Recolher Todos os DDDs' : 'Expandir Todos os DDDs';
    }};
  }}
}}

window.toggleDetIndicator = function(key) {{
  const rows = document.querySelectorAll('.det-sub-' + key);
  const ico = document.getElementById('ico_' + key);
  const anyHidden = [...rows].some(r => r.style.display === 'none');
  rows.forEach(r => {{
    r.style.display = anyHidden ? '' : 'none';
  }});
  if (ico) ico.textContent = anyHidden ? '▾' : '▸';
}};

/* ============ VISÃO 4 (PARTE B): TABELA ANALÍTICA ============ */
let detailPage = 1;
const PAGE_SIZE = 100;
function renderAnalytic(fRows) {{
  const tEl = document.getElementById('tblDetalhada');
  const q = (document.getElementById('detailSearch')?.value || '').toLowerCase().trim();

  let rows = fRows;
  if (q) {{
    rows = fRows.filter(r => {{
      const c = D.cidade[r[0]].toLowerCase();
      const g = D.grupo[r[1]].toLowerCase();
      const e = D.empresa[r[2]].toLowerCase();
      const u = D.uf[r[4]].toLowerCase();
      return c.includes(q) || g.includes(q) || e.includes(q) || u.includes(q);
    }});
  }}

  document.getElementById('detailRowsNote').textContent = `${{rows.length.toLocaleString('pt-BR')}} registros filtrados`;
  const totalPages = Math.max(1, Math.ceil(rows.length / PAGE_SIZE));
  if (detailPage > totalPages) detailPage = 1;

  document.getElementById('detailPageInfo').textContent = `Página ${{detailPage}} de ${{totalPages}} (exibindo ${{Math.min(rows.length, PAGE_SIZE)}} por página)`;

  const start = (detailPage - 1) * PAGE_SIZE;
  const pageRows = rows.slice(start, start + PAGE_SIZE);

  let html = `<thead><tr>
    <th class="l">Município</th>
    <th class="l">UF</th>
    <th>DDD</th>
    <th class="l">Grupo</th>
    <th class="l">Empresa / Provedor</th>
    <th class="l">Serviço</th>
    <th class="l">Tipo Cabo</th>
    <th class="l">Tecnologia</th>
    <th>jul/26</th>
    <th>ago/26</th>
    <th>Net Adds</th>
  </tr></thead><tbody>`;

  pageRows.forEach(r => {{
    const m = r[11];
    const j26 = m[12], a26 = m[13];
    const net = a26 - j26;
    html += `<tr>
      <td class="l">${{D.cidade[r[0]]}}</td>
      <td class="l">${{D.uf[r[4]]}}</td>
      <td>${{D.ddd[r[3]]}}</td>
      <td class="l">${{D.grupo[r[1]]}}</td>
      <td class="l">${{D.empresa[r[2]]}}</td>
      <td class="l">${{D.servico[r[5]]}}</td>
      <td class="l">${{D.tipo_cidade[r[6]]}}</td>
      <td class="l">${{D.tecnologia[r[9]]}}</td>
      <td>${{fmt(j26)}}</td>
      <td>${{fmt(a26)}}</td>
      <td class="${{net >= 0 ? 'pos' : 'neg'}}">${{net >= 0 ? '+' : ''}}${{fmt(net)}}</td>
    </tr>`;
  }});

  html += '</tbody>';
  tEl.innerHTML = html;
}}

/* ============ Exportação CSV ============ */
function exportCsv() {{
  const fRows = getFilteredRows();
  let csv = 'Municipio;UF;DDD;Grupo;Empresa;Servico;TipoCidade;TipoCliente;Tecnologia;jul26;ago26;NetAdds\\n';
  fRows.forEach(r => {{
    const m = r[11];
    const row = [
      D.cidade[r[0]], D.uf[r[4]], D.ddd[r[3]], D.grupo[r[1]], D.empresa[r[2]],
      D.servico[r[5]], D.tipo_cidade[r[6]], D.tipo_cliente[r[7]], D.tecnologia[r[9]],
      m[12], m[13], m[13] - m[12]
    ];
    csv += row.map(v => `"${{String(v).replace(/"/g, '""')}}"`).join(';') + '\\n';
  }});

  const blob = new Blob(['\\uFEFF' + csv], {{ type: 'text/csv;charset=utf-8;' }});
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = `market_share_residencial_${{new Date().toISOString().slice(0, 10)}}.csv`;
  link.click();
}}

/* ============ Eventos das Abas e DDD Pills ============ */
function initEvents() {{
  // Abas de Visão Principal
  const tabs = document.querySelectorAll('.tab-btn');
  tabs.forEach(t => {{
    t.onclick = () => {{
      tabs.forEach(b => b.classList.remove('on'));
      t.classList.add('on');
      currentTab = t.dataset.tab;
      document.querySelectorAll('.tab-content').forEach(c => {{ c.style.display = 'none'; }});
      if (currentTab === 'resumida') document.getElementById('viewResumida').style.display = '';
      else if (currentTab === 'isp') document.getElementById('viewIsp').style.display = '';
      else if (currentTab === 'municipio') document.getElementById('viewMunicipio').style.display = '';
      else if (currentTab === 'detalhada') document.getElementById('viewDetalhada').style.display = '';
      render();
    }};
  }});

  // Seletor de Dimensão da Visão Resumida (DDD / UF / Regional)
  const dimBtns = document.querySelectorAll('.tab-dim-btn');
  dimBtns.forEach(b => {{
    b.onclick = () => {{
      dimBtns.forEach(x => x.classList.remove('on'));
      b.classList.add('on');
      currentResumoDim = b.dataset.dim;
      renderResumida(getFilteredRows());
    }};
  }});

  // Filtro Rápido DDD
  const pills = document.querySelectorAll('.ddd-pill');
  pills.forEach(p => {{
    p.onclick = () => {{
      pills.forEach(b => b.classList.remove('act'));
      p.classList.add('act');
      const dVal = p.dataset.ddd;
      currentDddQuick = dVal;

      const dSelect = document.querySelector('select[data-dim="ddd"]');
      if (dVal === 'TODOS') {{
        delete sel.ddd;
        if (dSelect) [...dSelect.options].forEach(o => o.selected = false);
      }} else {{
        const idx = D.ddd.indexOf(dVal);
        if (idx >= 0) {{
          sel.ddd = new Set([idx]);
          if (dSelect) [...dSelect.options].forEach(o => o.selected = (+o.value === idx));
        }}
      }}
      render();
    }};
  }});

  // Busca na tabela analítica
  document.getElementById('detailSearch')?.addEventListener('input', () => {{
    detailPage = 1;
    renderAnalytic(getFilteredRows());
  }});

  // Modal Help
  const modal = document.getElementById('modalHelp');
  document.querySelectorAll('.hlp').forEach(btn => {{
    btn.onclick = () => {{
      const topic = btn.dataset.h;
      openHelp(topic);
    }};
  }});
  document.getElementById('helpClose').onclick = () => modal.classList.remove('on');
  modal.onclick = e => {{ if (e.target === modal) modal.classList.remove('on'); }};
}}

const HELP = {{
  filtros: `<h4>Gaveta de Filtros Retrátil</h4><p>Permite selecionar múltiplas opções simultaneamente em cada dimensão analítica. As opções disponíveis no cenário atual permanecem no topo da lista. Itens que não ocorrem no cenário selecionado são exibidos ao final em tom cinza e itálico.</p>`,
  kpis: `<h4>Indicadores Oficiais</h4><p>Calculados sobre a base de Banda Larga Fixa na Regional Norte para a Claro e players concorrentes. A liderança e o Market Share são obtidos diretamente dos relatórios de mercado com posição oficial da Anatel.</p>`,
  resumida: `<h4>Visão Resumida</h4><p>Quatro quadros analíticos (Market Share %, Net Adds, Base e Net Share %) comparando os principais players (Claro, Vivo, Tim, Oi, Sky) e o grupo Outros. Permite alternar a dimensão de abertura entre DDD, UF e Regional Total.</p>`,
  isp: `<h4>Visão ISP's</h4><p>Consolida todas as variações de Claro em uma única linha institucional. Separa as grandes operadoras nacionais dos provedores regionais independentes (ISPs), detalhando o Top 10 provedores com comparativos históricos completos (ago/25, jul/26, ago/26, MoM e YoY).</p>`,
  municipio: `<h4>Visão por Município Polo</h4><p>Demonstra o market share, adições líquidas e volume de acessos nos principais centros urbanos da Regional Norte.</p>`,
  detalhada: `<h4>Visão Detalhada</h4><p>Traz a matriz histórica mensal completa (14 meses) com 4 linhas analíticas por operadora (Base, Share %, Net Adds e Net Share %), acompanhada da Projeção de Ultrapassagem da Liderança e da base analítica individual com busca.</p>`,
  projecao: `<h4>Projeção de Ultrapassagem</h4><p>Analisa o gap de clientes entre a Claro e o líder do cenário atual, projetando as adições líquidas mensais necessárias para alcançar a liderança em horizontes de 12, 24, 36 e 48 meses.</p>`,
  grafico: `<h4>Evolução Histórica da Base</h4><p>Demonstra a série temporal de 14 meses (jul/25 a ago/26) da base de clientes das principais operadoras (Claro, Vivo, Tim, Oi/Nio) e do agrupamento de ISPs (Outros).</p>`,
  registros: `<h4>Registros Analíticos</h4><p>Base granular de dados filtrada pelo cenário ativo, permitindo busca e exportação completa para CSV.</p>`
}};

function openHelp(topic) {{
  const m = document.getElementById('modalHelp');
  document.getElementById('helpTitle').textContent = 'Ajuda: ' + topic.toUpperCase();
  document.getElementById('helpContent').innerHTML = HELP[topic] || '<p>Informações metodológicas sobre este bloco.</p>';
  m.classList.add('on');
}}

// Autenticação
async function initAuth() {{
  try {{
    const res = await fetch('/api/auth/me');
    if (res.ok) {{
      const u = await res.json();
      const el = document.getElementById('mktUserWidget');
      if (el && u.authenticated) {{
        const fn = u.nome_completo.split(' ')[0];
        el.innerHTML = `
          <span style="color:#fff;font-size:11.5px;font-weight:600;white-space:nowrap;background:rgba(255,255,255,.15);padding:4px 8px;border-radius:3px">${{fn}} (${{u.area}})</span>
          ${{u.is_admin ? '<a href="/admin/" style="background:rgba(255,255,255,.2);color:#fff;border:1px solid rgba(255,255,255,.4);padding:4px 8px;border-radius:3px;font-size:10.5px;font-weight:700;text-decoration:none">Admin</a>' : ''}}
          <button id="btnLogoutMkt" style="background:none;border:1px solid rgba(255,255,255,.3);color:#fff;padding:4px 8px;border-radius:3px;font-size:10.5px;cursor:pointer;font-weight:600">Sair</button>
        `;
        document.getElementById('btnLogoutMkt').addEventListener('click', async () => {{
          await fetch('/api/auth/logout', {{ method: 'POST' }});
          window.location.href = '/login/';
        }});
      }}
    }}
  }} catch (e) {{}}
}}

// Inicialização
document.addEventListener('DOMContentLoaded', () => {{
  buildFilterUI();
  initEvents();
  applyDefaultFilters();
  render();
  initAuth();
}});
</script>
<script src="/js/app-mobile.js"></script>
</body>
</html>"""

if __name__ == "__main__":
    build()
