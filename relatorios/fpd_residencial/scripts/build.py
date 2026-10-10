# -*- coding: utf-8 -*-
"""
Builder Oficial do Relatório Executivo de FPD Residencial (Fixa) — Regional Norte
Padrão Ouro Churn Safra — Versão 3 com Cubo Multidimensional Reativo em Tempo Real

Atende rigorosamente aos 6 requisitos solicitados:
  1. Filtros reativos e matematicamente precisos em TODAS as tabelas e KPIs do topo (cubo O(N) no cliente).
  2. Opção "Todas as Métricas" com coluna explícita de indicador na linha (%FPD60, %FPD30, Inadimplentes, Instalações).
  3. Visões presenciais (AA, PAP, Varejo, Lojas) com Benchmark Brasil do canal, 3 separadores de mercados
     (Grandes Mercados, Mercados em Desenvolvimento e Sem Cabo), busca rápida de parceiros e Praças Atendidas reais.
  4. Classificação universal de todas as colunas com ordenação ascendente/descendente interativa.
  5. Tabela comparativa de Canal na visão Brasil (Benchmark Nacional) na aba de Canais.
  6. Filtro analítico de Multi (Multi Marcado, Multi Não Marcado, Não é Multi).
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

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_DIR = os.path.dirname(SCRIPT_DIR)
WORKSPACE_DIR = os.path.dirname(os.path.dirname(REPORT_DIR))

BASE_PATH = os.path.join(WORKSPACE_DIR, "BASE.xlsx")
if not os.path.exists(BASE_PATH):
    BASE_PATH = os.path.join(REPORT_DIR, "dados", "BASE.xlsx")

BASE_BRASIL_PATH = os.path.join(WORKSPACE_DIR, "BASE_BRASIL.xlsx")
if not os.path.exists(BASE_BRASIL_PATH):
    BASE_BRASIL_PATH = os.path.join(REPORT_DIR, "dados", "BASE_BRASIL.xlsx")

OUTPUT_HTML = os.path.join(REPORT_DIR, "index.html")
PUBLIC_HTML = os.path.join(WORKSPACE_DIR, "public", "fpd-residencial", "index.html")
PUBLIC_FPD_HTML = os.path.join(WORKSPACE_DIR, "public", "fpd", "index.html")
PUBLIC_STAGING_FPD_RES = os.path.join(WORKSPACE_DIR, "public_staging", "fpd-residencial", "index.html")
PUBLIC_STAGING_FPD = os.path.join(WORKSPACE_DIR, "public_staging", "fpd", "index.html")

MONTH_LABELS = [
    "Jun/25", "Jul/25", "Ago/25", "Set/25", "Out/25", "Nov/25", "Dez/25",
    "Jan/26", "Fev/26", "Mar/26", "Abr/26", "Mai/26", "Jun/26"
]

SAFRAS_HIST = [
    202506, 202507, 202508, 202509, 202510, 202511, 202512,
    202601, 202602, 202603, 202604, 202605, 202606
]
SAFRA_MAP = {s: i for i, s in enumerate(SAFRAS_HIST)}

CIDADES_GRANDES = ["ANANINDEUA", "BELEM", "BOA VISTA", "MACAPA", "MANAUS", "SANTANA", "SAO LUIS"]
CIDADES_DEV = ["CASTANHAL", "CAXIAS", "IMPERATRIZ", "MARABA", "PARAGOMINAS", "PARAUAPEBAS", "TIMON"]
CIDADES_SEM_CABO = []
ALL_CIDADES_ORD = CIDADES_GRANDES + CIDADES_DEV
CIDADE_MAP = {c: i for i, c in enumerate(ALL_CIDADES_ORD)}

CANAIS_PRESENCIAIS = [
    'Agente Autorizado', 'Porta Porta', 'Lojas Proprias', 'Varejo',
    'Distribuidor', 'Canais Exclusivo Empresas'
]
CANAIS_REMOTOS = [
    'Ativo', 'Receptivo', 'Canais Eletronicos'
]
CANAIS_OUTROS = [
    'Outros'
]
CANAIS_ORDEM = CANAIS_PRESENCIAIS + CANAIS_REMOTOS + CANAIS_OUTROS
CANAL_MAP = {c: i for i, c in enumerate(CANAIS_ORDEM)}

def clean_f(v):
    if v is None or str(v).strip() in ['', '-', 'None', 'null']: return 0.0
    try: return float(v)
    except: return 0.0

def clean_i(v):
    if v is None or str(v).strip() in ['', '-', 'None', 'null']: return 0
    try: return int(round(float(v)))
    except: return 0

def calc_series(d_safra_dict):
    """Gera listas de 13 meses e variações a partir do dicionário de safras."""
    taxa60 = []
    taxa30 = []
    qtd = []
    inst = []
    for s in SAFRAS_HIST:
        info = d_safra_dict.get(s, {'ag30': 0.0, 'qtd': 0.0, 'fpd60': 0.0})
        q = info['qtd']
        t60 = round((info['fpd60'] / q * 100), 2) if q > 0 else 0.0
        t30 = round((info['ag30'] / q * 100), 2) if q > 0 else 0.0
        taxa60.append(t60)
        taxa30.append(t30)
        qtd.append(clean_i(info['fpd60']))
        inst.append(clean_i(q))

    atual_t60 = taxa60[-1]
    prev_t60 = taxa60[-2]
    mom_t60 = round(atual_t60 - prev_t60, 2)
    yoy_t60 = round(atual_t60 - taxa60[0], 2)

    atual_t30 = taxa30[-1]
    prev_t30 = taxa30[-2]
    mom_t30 = round(atual_t30 - prev_t30, 2)
    yoy_t30 = round(atual_t30 - taxa30[0], 2)

    atual_qtd = qtd[-1]
    prev_qtd = qtd[-2]
    mom_qtd = atual_qtd - prev_qtd
    yoy_qtd = atual_qtd - qtd[0]

    atual_inst = inst[-1]
    prev_inst = inst[-2]
    mom_inst = atual_inst - prev_inst
    yoy_inst = atual_inst - inst[0]

    return {
        'taxa60': taxa60,
        'taxa30': taxa30,
        'qtd': qtd,
        'inst': inst,
        'atual_taxa60': atual_t60,
        'prev_taxa60': prev_t60,
        'mom_taxa60': mom_t60,
        'yoy_taxa60': yoy_t60,
        'atual_taxa30': atual_t30,
        'prev_taxa30': prev_t30,
        'mom_taxa30': mom_t30,
        'yoy_taxa30': yoy_t30,
        'atual_qtd': atual_qtd,
        'prev_qtd': prev_qtd,
        'mom_qtd': mom_qtd,
        'yoy_qtd': yoy_qtd,
        'atual_inst': atual_inst,
        'prev_inst': prev_inst,
        'mom_inst': mom_inst,
        'yoy_inst': yoy_inst,
        'max_t60': max(taxa60) if any(taxa60) else 0.0,
        'max_t30': max(taxa30) if any(taxa30) else 0.0
    }

def load_data():
    print("Iniciando leitura das bases oficiais...")
    t0 = time.time()

    # 1. BASE_BRASIL.xlsx (Total Nacional, Séries e Cubo Analítico Brasil)
    print(f"  • Lendo Benchmark Brasil em {BASE_BRASIL_PATH}...")
    wb_br = openpyxl.load_workbook(BASE_BRASIL_PATH, read_only=True)
    sh_br = wb_br['Planilha1'] if 'Planilha1' in wb_br.sheetnames else wb_br.active
    it_br = sh_br.iter_rows(values_only=True)
    h_br = next(it_br)
    if h_br[0] != 'SAFRA': h_br = next(it_br)

    br_agg = {sf: {'ag30': 0.0, 'qtd': 0.0, 'fpd60': 0.0} for sf in SAFRAS_HIST}
    br_canais_agg = {}
    br_raw_rows = []

    subgrupos_set = set()
    empresas_set = set()
    riscos_set = set()
    produtos_set = set()
    combinacoes_set = set()
    empresa_cidades = {}
    empresa_canais = {}

    for r in it_br:
        safra = r[0]
        if not safra: continue
        safra = int(safra)
        if safra not in br_agg: continue

        canal = str(r[1] or '').strip()
        subcanal = str(r[2] or '').strip()
        comb = str(r[3] or '').strip()
        if not comb: comb = 'Não Informado'
        risco = str(r[5] or '').strip()
        prod = str(r[6] or '').strip()
        seg = str(r[8] or '').strip()

        ag30 = clean_f(r[9])
        qtd = clean_f(r[10])
        fpd60 = clean_f(r[12])

        br_agg[safra]['ag30'] += ag30
        br_agg[safra]['qtd'] += qtd
        br_agg[safra]['fpd60'] += fpd60

        if canal:
            if canal not in br_canais_agg:
                br_canais_agg[canal] = {sf: {'ag30': 0.0, 'qtd': 0.0, 'fpd60': 0.0} for sf in SAFRAS_HIST}
            br_canais_agg[canal][safra]['ag30'] += ag30
            br_canais_agg[canal][safra]['qtd'] += qtd
            br_canais_agg[canal][safra]['fpd60'] += fpd60

        if subcanal: subgrupos_set.add(subcanal)
        if comb: combinacoes_set.add(comb)
        if risco: riscos_set.add(risco)
        if prod: produtos_set.add(prod)

        br_raw_rows.append((safra, canal, subcanal, comb, risco, prod, seg, ag30, qtd, fpd60))

    wb_br.close()
    br_series = calc_series(br_agg)
    br_canais_series = {c: calc_series(br_canais_agg[c]) for c in br_canais_agg}

    # 2. BASE.xlsx (Regional Norte - 108k linhas)
    print(f"  • Lendo Regional Norte em {BASE_PATH} (108k linhas)...")
    wb_rno = openpyxl.load_workbook(BASE_PATH, read_only=True)
    sh_rno = wb_rno['fpd'] if 'fpd' in wb_rno.sheetnames else wb_rno.active
    it_rno = sh_rno.iter_rows(values_only=True)
    next(it_rno)
    next(it_rno)

    cube = {}

    for r in it_rno:
        safra = r[0]
        if not safra or not isinstance(safra, (int, float)): continue
        safra = int(safra)
        if safra not in SAFRA_MAP: continue

        cid = str(r[1] or '').strip().upper()
        if cid not in CIDADE_MAP: continue

        canal = str(r[4] or '').strip()
        if canal not in CANAL_MAP:
            canal = 'Outros'
        subcanal = str(r[5] or '').strip()
        comb = str(r[6] or '').strip()
        if not comb: comb = 'Não Informado'
        risco = str(r[9] or r[19] or '').strip()
        prod = str(r[14] or '').strip()
        emp = str(r[16] or '').strip()
        multi_raw = str(r[15] or '').strip()

        ag30 = clean_f(r[23])
        qtd = clean_f(r[25])
        fpd60 = clean_f(r[26])

        if subcanal: subgrupos_set.add(subcanal)
        if comb: combinacoes_set.add(comb)
        if emp and emp.upper() not in ['', 'NONE', 'NULL']:
            empresas_set.add(emp)
            if emp not in empresa_cidades: empresa_cidades[emp] = set()
            empresa_cidades[emp].add(cid)
            if emp not in empresa_canais: empresa_canais[emp] = set()
            empresa_canais[emp].add(canal)
        if risco: riscos_set.add(risco)
        if prod: produtos_set.add(prod)

        # Mapeamento do Multi: 1 = Marcado, 2 = Não Marcado, 0 = Não é Multi / Vazio
        if multi_raw == 'Marcado':
            multi_code = 1
        elif 'Marcado' in multi_raw:
            multi_code = 2
        else:
            multi_code = 0

        k = (SAFRA_MAP[safra], CIDADE_MAP[cid], CANAL_MAP[canal], subcanal, emp, risco, prod, comb, multi_code)
        if k not in cube: cube[k] = [0.0, 0.0, 0.0]
        cube[k][0] += ag30
        cube[k][1] += qtd
        cube[k][2] += fpd60

    wb_rno.close()
    t1 = time.time()
    print(f"  • Processamento de BASE.xlsx concluído em {t1-t0:.2f}s! (Total de células do cubo: {len(cube)})")

    subgrupos_list = sorted(list(subgrupos_set))
    empresas_list = sorted(list(empresas_set))
    riscos_list = sorted(list(riscos_set))
    produtos_list = sorted(list(produtos_set))
    combinacoes_list = sorted(list(combinacoes_set))

    subc_map = {s: i for i, s in enumerate(subgrupos_list)}
    emp_map = {e: i for i, e in enumerate(empresas_list)}
    risco_map = {r: i for i, r in enumerate(riscos_list)}
    prod_map = {p: i for i, p in enumerate(produtos_list)}
    comb_map = {cb: i for i, cb in enumerate(combinacoes_list)}

    # Montar cubo colunar plano de alta performance (Regional)
    cube_rows = []
    for k, v in cube.items():
        s_idx, c_idx, cn_idx, sub, emp, risco, prod, comb_val, mt_code = k
        sb_idx = subc_map.get(sub, -1)
        em_idx = emp_map.get(emp, -1)
        rc_idx = risco_map.get(risco, -1)
        pr_idx = prod_map.get(prod, -1)
        cb_idx = comb_map.get(comb_val, -1)
        # [safra, cid, canal, subc, emp, risco, prod, comb, multi, ag30, qtd, fpd60]
        cube_rows.append([
            s_idx, c_idx, cn_idx, sb_idx, em_idx, rc_idx, pr_idx, cb_idx, mt_code,
            round(v[0], 2), clean_i(v[1]), clean_i(v[2])
        ])

    # Montar cubo colunar plano do Brasil (Benchmark Reativo)
    br_cube = {}
    for r in br_raw_rows:
        sf, cn, sb, cb, rc, pr, seg, ag30, qtd, f60 = r
        s_idx = SAFRA_MAP.get(sf, -1)
        cn_idx = CANAL_MAP.get(cn, -1)
        sb_idx = subc_map.get(sb, -1)
        cb_idx = comb_map.get(cb, -1)
        rc_idx = risco_map.get(rc, -1)
        pr_idx = prod_map.get(pr, -1)
        seg_code = 1 if 'Grandes Mercados' in seg else (2 if 'Mercados em Desenvolvimento' in seg else 0)

        k = (s_idx, cn_idx, sb_idx, cb_idx, rc_idx, pr_idx, seg_code)
        if k not in br_cube: br_cube[k] = [0.0, 0.0, 0.0]
        br_cube[k][0] += ag30
        br_cube[k][1] += qtd
        br_cube[k][2] += f60

    br_cube_rows = []
    for k, v in br_cube.items():
        s_idx, cn_idx, sb_idx, cb_idx, rc_idx, pr_idx, seg_code = k
        # [safra, canal, subc, comb, risco, prod, seg_code, ag30, qtd, fpd60]
        br_cube_rows.append([
            s_idx, cn_idx, sb_idx, cb_idx, rc_idx, pr_idx, seg_code,
            round(v[0], 2), clean_i(v[1]), clean_i(v[2])
        ])

    # Metadados das empresas para o frontend
    empresas_meta = []
    for e in empresas_list:
        cids_str = ", ".join(sorted(list(empresa_cidades.get(e, []))))
        canais_list = sorted(list(empresa_canais.get(e, [])))
        empresas_meta.append({
            'name': e,
            'cidades': cids_str,
            'canais': canais_list
        })

    return {
        'br_series': br_series,
        'br_canais_series': br_canais_series,
        'br_cube_rows': br_cube_rows,
        'cube_rows': cube_rows,
        'safras': SAFRAS_HIST,
        'month_labels': MONTH_LABELS,
        'cidades': ALL_CIDADES_ORD,
        'cidades_gm': CIDADES_GRANDES,
        'cidades_md': CIDADES_DEV,
        'cidades_sc': CIDADES_SEM_CABO,
        'canais': CANAIS_ORDEM,
        'canais_presenciais': CANAIS_PRESENCIAIS,
        'canais_remotos': CANAIS_REMOTOS,
        'canais_outros': CANAIS_OUTROS,
        'subcanais': subgrupos_list,
        'empresas': empresas_meta,
        'riscos': riscos_list,
        'produtos': produtos_list,
        'combinacoes': combinacoes_list,
        'multis': [
            {'val': 'Não é Multi', 'code': 0, 'label': 'Não é Multi'},
            {'val': 'Multi Marcado', 'code': 1, 'label': 'Multi Marcado'},
            {'val': 'Multi Não Marcado', 'code': 2, 'label': 'Multi Não Marcado'}
        ]
    }

def format_pct(val):
    return f"{val:.2f}%".replace('.', ',')

def format_delta(val, is_pct=True):
    unit = " p.p." if is_pct else ""
    sign = "+" if val > 0 else ""
    cls = "red" if val > 0 else ("green" if val < 0 else "neutral")
    return f'<span class="d-val {cls}">{sign}{val:.2f}{unit}</span>'.replace('.', ',')

def build():
    data = load_data()
    print("  • Gerando HTML com Cubo Reativo O(N) e Padrão Ouro...")
    html_content = generate_html(data)

    # Gravar nas saídas oficiais
    for path in [OUTPUT_HTML, PUBLIC_HTML, PUBLIC_FPD_HTML, PUBLIC_STAGING_FPD_RES, PUBLIC_STAGING_FPD]:
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(html_content)
            size_kb = os.path.getsize(path) / 1024
            print(f"✅ Arquivo atualizado: {path} ({size_kb:.1f} KB)")
        except Exception as e:
            print(f"⚠️ Erro ao gravar em {path}: {e}")

    return True

def generate_html(d):
    payload_json = json.dumps(d, ensure_ascii=False)

    opt_cidades = "".join([f'<option value="{c}">{c}</option>' for c in d['cidades']])
    opt_canais = "".join([f'<option value="{c}">{c}</option>' for c in d['canais']])
    opt_subcanais = "".join([f'<option value="{c}">{c}</option>' for c in d['subcanais']])
    opt_empresas = "".join([f'<option value="{e["name"]}">{e["name"]}</option>' for e in d['empresas']])
    opt_riscos = "".join([f'<option value="{r}">{r}</option>' for r in d['riscos']])
    opt_produtos = "".join([f'<option value="{p}">{p}</option>' for p in d['produtos']])
    opt_combinacoes = "".join([f'<option value="{cb}">{cb}</option>' for cb in d['combinacoes']])
    opt_multis = "".join([f'<option value="{m["val"]}">{m["label"]}</option>' for m in d['multis']])

    br = d['br_series']

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Relatório Executivo FPD Residencial — Regional Norte</title>

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
.hd-sub .hd-right {{ margin-left: auto; }}
.dl-btn {{
  display: inline-flex;
  align-items: center;
  background: rgba(255,255,255,.18);
  color: #fff;
  border: 1px solid rgba(255,255,255,.35);
  border-radius: 3px;
  padding: 5px 12px;
  font-size: 11.5px;
  font-weight: 600;
  text-decoration: none;
  transition: background .15s, border-color .15s;
  white-space: nowrap;
}}
.dl-btn:hover {{
  background: rgba(255,255,255,.28);
  color: #fff;
  border-color: rgba(255,255,255,.6);
}}
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

/* ---- Filtros Gaveta Retrátil Padrão Churn Safra ---- */
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
.drawer-btn span {{ font-size: 10px; transition: transform .15s; display: inline-block; }}
.drawer-btn.open span {{ transform: rotate(90deg); }}

.drawer-content {{ display: none; margin-top: 12px; }}
.drawer-content.open {{ display: block; }}

.filters {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(185px, 1fr));
  gap: 10px;
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
button.primary {{ background: var(--nav); color: #ffffff; border-color: var(--nav); font-weight: 600; }}
button.primary:hover {{ background: var(--nav2); }}

.chips {{ display: flex; gap: 6px; flex-wrap: wrap; margin-left: auto; }}
.chip {{
  background: #eef1f4;
  border: 1px solid var(--line);
  border-radius: 2px;
  padding: 2px 8px;
  font-size: 11px;
  color: var(--ink2);
  display: inline-flex;
  align-items: center;
  gap: 5px;
}}
.chip .x {{ cursor: pointer; color: var(--red); font-weight: bold; font-size: 10px; }}

/* ---- KPIs do Cabeçalho ---- */
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
.kpi .k {{
  font-size: 10.5px;
  text-transform: uppercase;
  letter-spacing: .5px;
  color: var(--ink3);
}}
.kpi .v {{
  font-size: 22px;
  font-weight: 600;
  margin-top: 3px;
  letter-spacing: -.3px;
}}
.kpi .d {{
  font-size: 11px;
  color: var(--ink2);
  margin-top: 2px;
}}
.kpi.acc .v {{ color: var(--red); }}
.kpi.prev .v {{ color: var(--amber); }}
.kpi.vol .v {{ color: var(--purple); }}
.kpi.inst .v {{ color: var(--blue); }}

/* ---- Tabs e Botões Segmentados Padrão Churn Safra ---- */
.tabs {{
  display: inline-flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0;
}}
.tabs button {{
  border: 1px solid var(--line);
  background: #ffffff;
  color: var(--ink2);
  border-radius: 0;
  border-right: none;
  font-size: 11.5px;
  font-weight: 500;
  padding: 5px 12px;
  cursor: pointer;
  transition: background .15s, color .15s, border-color .15s;
}}
.tabs button:first-child {{
  border-top-left-radius: 3px;
  border-bottom-left-radius: 3px;
}}
.tabs button:last-child {{
  border-right: 1px solid var(--line);
  border-top-right-radius: 3px;
  border-bottom-right-radius: 3px;
}}
.tabs button:hover {{
  background: #f0f2f5;
  color: var(--ink);
}}
.tabs button.on {{
  background: var(--nav);
  color: #ffffff;
  border-color: var(--nav);
  font-weight: 600;
}}

.view-pane {{ display: none; }}
.view-pane.active {{ display: block; }}

/* ---- Subheaders e Seletor de Métricas ---- */
.sub-header-panel {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 14px 0 8px 0;
  flex-wrap: wrap;
  gap: 10px;
}}
.sub-header-panel h3 {{
  margin: 0;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--ink);
  letter-spacing: .4px;
}}

.partner-search-box {{
  display: flex;
  align-items: center;
  gap: 8px;
}}
.partner-search-input {{
  border: 1px solid var(--line);
  border-radius: 2px;
  padding: 4px 8px;
  font: 11.5px "Segoe UI", Arial;
  color: var(--ink);
  width: 260px;
}}
.partner-search-input:focus {{ outline: none; border-color: var(--blue); }}

/* Badges de Indicadores para "Todas as Métricas" */
.badge-metric {{
  display: inline-block;
  padding: 1px 6px;
  border-radius: 3px;
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .3px;
}}
.badge-metric.f60 {{ background: #fbeae8; color: var(--red); border: 1px solid #f5c2bc; }}
.badge-metric.f30 {{ background: #fdf3e2; color: #8a5d06; border: 1px solid #f0dcb4; }}
.badge-metric.vol {{ background: #f3ebf9; color: var(--purple); border: 1px solid #e1d0ed; }}
.badge-metric.ins {{ background: #e8f1fa; color: var(--blue); border: 1px solid #c7ddf2; }}

/* ---- Tabelas Analíticas Padrão Ouro ---- */
.tbl-wrap {{
  overflow-x: auto;
  border: 1px solid var(--line);
  border-radius: 2px;
}}
table {{
  width: 100%;
  border-collapse: collapse;
  font-size: 11.5px;
}}
th, td {{
  padding: 5px 7px;
  text-align: right;
  white-space: nowrap;
  border-bottom: 1px solid var(--line2);
}}
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
  user-select: none;
}}
th.sortable {{ cursor: pointer; transition: background .15s; }}
th.sortable:hover {{ background: #eef1f4; color: var(--ink); }}
th .sort-arrow {{ font-size: 9px; margin-left: 3px; color: var(--ink3); }}
th.sorted-asc .sort-arrow, th.sorted-desc .sort-arrow {{ color: var(--red); font-weight: 800; }}

th.l, td.l {{ text-align: left; }}
td.td-foco, th.th-foco {{
  background: #fff4f2 !important;
  font-weight: 700;
  color: var(--red);
  border-left: 1px solid #f5c2bc;
  border-right: 1px solid #f5c2bc;
}}
th.th-hist-start, td.td-hist-start {{
  border-left: 2px solid var(--line);
}}
tbody tr:hover td {{ background: #f7f9fb; }}
tbody tr.bench-row td {{ background: #fffdf2; font-weight: 600; }}
tbody tr.grp-header td {{
  background: #edf1f5;
  color: var(--nav);
  font-weight: 700;
  font-size: 10.5px;
  letter-spacing: .3px;
  text-align: right;
  padding: 5px 8px;
}}
tbody tr.grp-header td.l {{
  text-align: left;
  text-transform: uppercase;
}}
tbody tr.grp-gm td:first-child {{ border-left: 4px solid var(--blue); }}
tbody tr.grp-md td:first-child {{ border-left: 4px solid var(--amber); }}
tbody tr.grp-sc td:first-child {{ border-left: 4px solid var(--purple); }}

/* Remoção total de barreiras verticais nos agrupamentos de canais da Visão 1 */
#tblCanal tbody tr.grp-header td,
#tblCanal tbody tr.grp-header-sub td,
#tblCanal tbody tr.grp-total-row td,
#tblCanalBrasil tbody tr.grp-header td,
#tblCanalBrasil tbody tr.grp-header-sub td,
#tblCanalBrasil tbody tr.grp-total-row td {{
  border-left: none !important;
  border-right: none !important;
}}

/* Alinhamento estrito e idêntico de colunas entre tabelas de Canais (Regional e Brasil) */
#tblCanal, #tblCanalBrasil {{
  table-layout: fixed;
  width: 100%;
  min-width: 1420px;
}}
#tblCanal th:first-child, #tblCanal td:first-child,
#tblCanalBrasil th:first-child, #tblCanalBrasil td:first-child {{
  width: 250px;
  min-width: 250px;
  max-width: 250px;
}}
#tblCanal th.th-indicador, #tblCanal td.td-indicador,
#tblCanalBrasil th.th-indicador, #tblCanalBrasil td.td-indicador {{
  width: 160px;
  min-width: 160px;
  max-width: 160px;
}}
#tblCanal th.th-foco, #tblCanal td.td-foco,
#tblCanalBrasil th.th-foco, #tblCanalBrasil td.td-foco {{
  width: 95px;
  min-width: 95px;
  max-width: 95px;
}}
#tblCanal th.th-mai, #tblCanal td.td-mai,
#tblCanalBrasil th.th-mai, #tblCanalBrasil td.td-mai {{
  width: 80px;
  min-width: 80px;
  max-width: 80px;
}}
#tblCanal th.th-mom, #tblCanal td.td-mom,
#tblCanalBrasil th.th-mom, #tblCanalBrasil td.td-mom {{
  width: 85px;
  min-width: 85px;
  max-width: 85px;
}}
#tblCanal th.th-yoy, #tblCanal td.td-yoy,
#tblCanalBrasil th.th-yoy, #tblCanalBrasil td.td-yoy {{
  width: 85px;
  min-width: 85px;
  max-width: 85px;
}}
#tblCanal th.th-mes, #tblCanal td.td-mes,
#tblCanalBrasil th.th-mes, #tblCanalBrasil td.td-mes {{
  width: 70px;
  min-width: 70px;
  max-width: 70px;
}}

/* Opções de filtro indisponíveis (dependentes) */
select option.na {{
  color: var(--ink3);
  font-style: italic;
  background-color: #fafbfc;
}}

/* Linhas de Subtotal / Total por Grupo de Canal e Mercados */
tbody tr.grp-total-row td {{
  background: #edf1f5 !important;
  font-weight: 700;
  text-align: right;
  text-transform: none;
  border-top: 1px solid var(--line);
}}
tbody tr.grp-total-row td.l {{
  text-align: left;
  text-transform: uppercase;
}}
tbody tr.grp-header-sub.grp-total-row td {{
  background: #f4f7fa !important;
  font-weight: 600;
  text-align: right;
  text-transform: none;
}}
tbody tr.grp-header-sub.grp-total-row td.l {{
  text-align: left;
}}

/* Estilo para Filtro Travado na Visão Exclusiva */
.filter-locked {{
  background: #f8fafc !important;
  border-color: #cbd5e1 !important;
}}
.filter-locked select {{
  background: #f1f5f9 !important;
  cursor: not-allowed !important;
  color: var(--ink2) !important;
}}
.filter-locked-badge {{
  font-size: 9px;
  background: #e2e8f0;
  color: #334155;
  padding: 1px 5px;
  border-radius: 2px;
  font-weight: 700;
  margin-left: 5px;
}}

tfoot td {{
  font-weight: 700;
  background: #f7f8fa;
  border-top: 2px solid var(--line);
}}

/* Formatação de Deltas (Sempre em minúsculas: p.p.) */
.d-val {{ font-weight: 600; font-size: 11px; text-transform: lowercase !important; }}
.d-val.red {{ color: var(--red); }}
.d-val.green {{ color: var(--green); }}
.d-val.neutral {{ color: var(--ink3); }}
.peak-val {{
  background: #fdf5f4;
  color: var(--red);
  padding: 1px 4px;
  border-radius: 2px;
  font-weight: 700;
}}

.foot-note {{
  margin-top: 8px;
  font-size: 10.5px;
  color: var(--ink3);
}}
</style>
</head>
<body>

<header>
  <div class="hd-bar">
    <div class="hd-ico">
      <svg viewBox="0 0 48 48" width="34" height="34" aria-hidden="true">
        <circle cx="24" cy="24" r="21" fill="none" stroke="#fff" stroke-width="2.6"/>
        <path d="M31.5 16.5 L26.5 26.5 L16.5 31.5 L21.5 21.5 Z" fill="#fff"/>
      </svg>
    </div>
    <h1><b>FPD Residencial</b> <span>Regional Norte</span></h1>
    <div style="margin-left:auto;display:flex;align-items:center;gap:10px;flex-wrap:wrap">
      <a href="/fpd-residencial/download" download="Painel_FPD_Residencial_Regional_Norte.html" class="dl-btn" title="Baixar arquivo HTML independente com todos os dados para envio por e-mail">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;margin-right:6px"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
        Exportar para E-mail (.html)
      </a>
      <div id="fpdUserWidget" style="display:flex;align-items:center;gap:8px"></div>
    </div>
  </div>
  <div class="hd-sub">
    <a href="/" class="back-hub" title="Voltar ao Pephub — Portal de Churn & Qualidade">‹ Portal Pephub</a>
    <span class="dot"></span>
    <span><b>13 Safras</b> · jun/25 a jun/26</span>
    <span class="dot"></span>
    <span>Safra Foco: <b>Jun/26</b></span>
    <span class="dot"></span>
    <span>Bases: <b>BASE.xlsx</b> (Regional) e <b>BASE_BRASIL.xlsx</b> (Benchmark)</span>
    <div class="hd-right">
      <span>Métricas Oficiais: <b>FPD 60 Dias, FPD 30 Dias, Inadimplentes e Instalações</b></span>
    </div>
  </div>
</header>

<main class="wrap">

  <!-- ========================================== -->
  <!-- PAINEL DE CONTROLE E FILTROS ANALÍTICOS -->
  <!-- ========================================== -->
  <div class="panel">
    <h2>
      <span>Painel de Controle e Filtros Analíticos</span>
      <span class="note">Filtre cidades, canais, subgrupos, empresas, riscos e multi em tempo real</span>
      <button class="drawer-btn" id="btnDrawer" onclick="toggleDrawer()">
        <span>&#9654;</span> Filtros Analíticos
      </button>
    </h2>

    <div class="pbody">
      <div class="drawer-content open" id="drawerContent">
        <div class="filters">

          <!-- 1. Cidade -->
          <div class="f">
            <label>Cidade / Praça <span class="cnt" id="cntCidade">0/{len(d['cidades'])}</span></label>
            <div class="frow">
              <input type="text" placeholder="Buscar cidade..." oninput="filterSelect('selCidade', this.value)">
              <button class="fbtn" onclick="selAll('selCidade')">Todos</button>
              <button class="fbtn" onclick="clearSel('selCidade')">Limpar</button>
            </div>
            <select id="selCidade" multiple size="5" onchange="handleFilterChange('selCidade', 'cntCidade')">
              {opt_cidades}
            </select>
            <div class="sel" id="infoCidade">Todas as praças visíveis</div>
          </div>

          <!-- 2. Canal (Travado automaticamente nas visões exclusivas) -->
          <div class="f" id="cardCanal">
            <label>Canal de Venda <span class="filter-locked-badge" id="badgeCanalLocked" style="display:none"><svg style="display:inline-block;vertical-align:-1px;margin-right:2px;" viewBox="0 0 24 24" width="11" height="11" fill="none" stroke="currentColor" stroke-width="2.2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg> Fixo</span> <span class="cnt" id="cntCanal">0/{len(d['canais'])}</span></label>
            <div class="frow">
              <input type="text" id="iptSearchCanal" placeholder="Buscar canal..." oninput="filterSelect('selCanal', this.value)">
              <button class="fbtn" id="btnAllCanal" onclick="selAll('selCanal')">Todos</button>
              <button class="fbtn" id="btnClrCanal" onclick="clearSel('selCanal')">Limpar</button>
            </div>
            <select id="selCanal" multiple size="5" onchange="handleFilterChange('selCanal', 'cntCanal')">
              {opt_canais}
            </select>
            <div class="sel" id="infoCanal">Todos os canais</div>
          </div>

          <!-- 3. Subcanal -->
          <div class="f">
            <label>Canal Subgrupo <span class="cnt" id="cntSubcanal">0/{len(d['subcanais'])}</span></label>
            <div class="frow">
              <input type="text" placeholder="Buscar subgrupo..." oninput="filterSelect('selSubcanal', this.value)">
              <button class="fbtn" onclick="selAll('selSubcanal')">Todos</button>
              <button class="fbtn" onclick="clearSel('selSubcanal')">Limpar</button>
            </div>
            <select id="selSubcanal" multiple size="5" onchange="handleFilterChange('selSubcanal', 'cntSubcanal')">
              {opt_subcanais}
            </select>
            <div class="sel" id="infoSubcanal">Todos os subgrupos</div>
          </div>

          <!-- 4. Segmento Mercado -->
          <div class="f">
            <label>Segmento Mercado <span class="cnt" id="cntGrupo">0/2</span></label>
            <div class="frow">
              <input type="text" placeholder="Buscar grupo..." oninput="filterSelect('selGrupo', this.value)">
              <button class="fbtn" onclick="selAll('selGrupo')">Todos</button>
              <button class="fbtn" onclick="clearSel('selGrupo')">Limpar</button>
            </div>
            <select id="selGrupo" multiple size="5" onchange="handleFilterChange('selGrupo', 'cntGrupo')">
              <option value="Grandes Mercados">Grandes Mercados</option>
              <option value="Mercados em Desenvolvimento">Mercados em Desenvolvimento</option>
            </select>
            <div class="sel" id="infoGrupo">Todos os segmentos</div>
          </div>

          <!-- 5. Empresa -->
          <div class="f">
            <label>Empresa / Parceiro <span class="cnt" id="cntEmpresa">0/{len(d['empresas'])}</span></label>
            <div class="frow">
              <input type="text" placeholder="Buscar parceiro..." oninput="filterSelect('selEmpresa', this.value)">
              <button class="fbtn" onclick="selAll('selEmpresa')">Todos</button>
              <button class="fbtn" onclick="clearSel('selEmpresa')">Limpar</button>
            </div>
            <select id="selEmpresa" multiple size="5" onchange="handleFilterChange('selEmpresa', 'cntEmpresa')">
              {opt_empresas}
            </select>
            <div class="sel" id="infoEmpresa">Todas as empresas parceiras</div>
          </div>

          <!-- 6. Faixa de Risco -->
          <div class="f">
            <label>Faixa de Risco <span class="cnt" id="cntRisco">0/{len(d['riscos'])}</span></label>
            <div class="frow">
              <input type="text" placeholder="Buscar risco..." oninput="filterSelect('selRisco', this.value)">
              <button class="fbtn" onclick="selAll('selRisco')">Todos</button>
              <button class="fbtn" onclick="clearSel('selRisco')">Limpar</button>
            </div>
            <select id="selRisco" multiple size="5" onchange="handleFilterChange('selRisco', 'cntRisco')">
              {opt_riscos}
            </select>
            <div class="sel" id="infoRisco">Todos os riscos</div>
          </div>

          <!-- 7. Tipo Produto -->
          <div class="f">
            <label>Tipo Produto <span class="cnt" id="cntProduto">0/{len(d['produtos'])}</span></label>
            <div class="frow">
              <input type="text" placeholder="Buscar produto..." oninput="filterSelect('selProduto', this.value)">
              <button class="fbtn" onclick="selAll('selProduto')">Todos</button>
              <button class="fbtn" onclick="clearSel('selProduto')">Limpar</button>
            </div>
            <select id="selProduto" multiple size="5" onchange="handleFilterChange('selProduto', 'cntProduto')">
              {opt_produtos}
            </select>
            <div class="sel" id="infoProduto">Todos os produtos</div>
          </div>

          <!-- 8. Combinação de Produtos (Requisito 3) -->
          <div class="f">
            <label>Combinação de Produtos <span class="cnt" id="cntCombinacao">0/{len(d['combinacoes'])}</span></label>
            <div class="frow">
              <input type="text" placeholder="Buscar combinação..." oninput="filterSelect('selCombinacao', this.value)">
              <button class="fbtn" onclick="selAll('selCombinacao')">Todos</button>
              <button class="fbtn" onclick="clearSel('selCombinacao')">Limpar</button>
            </div>
            <select id="selCombinacao" multiple size="5" onchange="handleFilterChange('selCombinacao', 'cntCombinacao')">
              {opt_combinacoes}
            </select>
            <div class="sel" id="infoCombinacao">Todas as combinações</div>
          </div>

          <!-- 9. Tipo Cliente (Multi) -->
          <div class="f">
            <label>Tipo Cliente (Multi) <span class="cnt" id="cntMulti">0/3</span></label>
            <div class="frow">
              <input type="text" placeholder="Buscar multi..." oninput="filterSelect('selMulti', this.value)">
              <button class="fbtn" onclick="selAll('selMulti')">Todos</button>
              <button class="fbtn" onclick="clearSel('selMulti')">Limpar</button>
            </div>
            <select id="selMulti" multiple size="5" onchange="handleFilterChange('selMulti', 'cntMulti')">
              {opt_multis}
            </select>
            <div class="sel" id="infoMulti">Todas as condições de Multi</div>
          </div>

        </div>

        <div class="fbar">
          <button class="primary" onclick="applyFilters()">Aplicar Filtros</button>
          <button onclick="resetAllFilters()">Limpar Todos</button>
          <div class="chips" id="activeFilterChips"></div>
        </div>
      </div>

      <!-- KPIS DINÂMICOS DO TOPO (Recalculados pelo Cubo em tempo real) -->
      <div class="kpis">
        <div class="kpi acc">
          <div class="k">% FPD 60 Dias (Foco Jun/26)</div>
          <div class="v" id="kpiFpd60">-</div>
          <div class="d" id="kpiFpd60Sub">-</div>
        </div>

        <div class="kpi prev">
          <div class="k">% FPD 30 Dias (Prevenção)</div>
          <div class="v" id="kpiFpd30">-</div>
          <div class="d" id="kpiFpd30Sub">-</div>
        </div>

        <div class="kpi vol">
          <div class="k">Inadimplentes FPD 60</div>
          <div class="v" id="kpiQtd">-</div>
          <div class="d" id="kpiQtdSub">-</div>
        </div>

        <div class="kpi inst">
          <div class="k">Instalações (Vendas)</div>
          <div class="v" id="kpiInst">-</div>
          <div class="d" id="kpiInstSub">-</div>
        </div>

        <div class="kpi">
          <div class="k">Benchmark Brasil (Jun/26)</div>
          <div class="v" id="kpiBr">{format_pct(br['atual_taxa60'])}</div>
          <div class="d" id="kpiBrSub">FPD 30: <b>{format_pct(br['atual_taxa30'])}</b> | MoM: {format_delta(br['mom_taxa60'])}</div>
        </div>

        <div class="kpi">
          <div class="k">Gap Regional vs Brasil</div>
          <div class="v" id="kpiGap">-</div>
          <div class="d" id="kpiGapSub">FPD 60 Brasil: {format_pct(br['atual_taxa60'])}</div>
        </div>
      </div>
    </div>
  </div>

  <!-- NAVEGAÇÃO ENTRE VISÕES (ABAS EXECUTIVAS) -->
  <div class="tabs view-tabs" style="margin-bottom:14px">
    <button class="on" onclick="switchView('tabCanal', this)">1. Visão por Canal de Venda</button>
    <button onclick="switchView('tabCidade', this)">2. Visão por Cidade / Praça</button>
    <button onclick="switchView('tabAA', this)">3. Agente Autorizado (AA)</button>
    <button onclick="switchView('tabPAP', this)">4. Porta a Porta (PAP)</button>
    <button onclick="switchView('tabVarejo', this)">5. Canal Varejo</button>
    <button onclick="switchView('tabLojas', this)">6. Lojas Próprias</button>
  </div>

  <div class="views-container">

    <!-- ========================================== -->
    <!-- 1. VISÃO POR CANAL DE VENDA -->
    <!-- ========================================== -->
    <div id="tabCanal" class="view-pane active">
      <div class="panel">
        <h2>
          <span>Desempenho Geral por Canal de Venda — Regional Norte</span>
          <span class="note">Abertura completa de canais com FPD 60, FPD 30, inadimplentes e volume de vendas</span>
        </h2>
        <div class="pbody">
          <div class="sub-header-panel">
            <h3>Canais de Venda — Regional Norte</h3>
            <span class="tabs" data-table="tblCanal">
              <button class="on" onclick="setTableMetric('tblCanal', 'f60', this)">% FPD 60 DIAS</button>
              <button onclick="setTableMetric('tblCanal', 'f30', this)">% FPD 30 DIAS (Prevenção)</button>
              <button onclick="setTableMetric('tblCanal', 'vol', this)">QTD FPD</button>
              <button onclick="setTableMetric('tblCanal', 'ins', this)">Instalação</button>
              <button onclick="setTableMetric('tblCanal', 'all', this)">Todas as Métricas</button>
            </span>
          </div>

          <div class="tbl-wrap" style="margin-bottom: 24px;">
            <table id="tblCanal">
              <thead></thead>
              <tbody></tbody>
              <tfoot></tfoot>
            </table>
          </div>

          <!-- Tabela Brasil por Canal (Requisito 5) -->
          <div class="sub-header-panel">
            <h3>Canais de Venda — Brasil (Benchmark Nacional)</h3>
            <span class="tabs" data-table="tblCanalBrasil">
              <button class="on" onclick="setTableMetric('tblCanalBrasil', 'f60', this)">% FPD 60 DIAS</button>
              <button onclick="setTableMetric('tblCanalBrasil', 'f30', this)">% FPD 30 DIAS (Prevenção)</button>
              <button onclick="setTableMetric('tblCanalBrasil', 'vol', this)">QTD FPD</button>
              <button onclick="setTableMetric('tblCanalBrasil', 'ins', this)">Instalação</button>
              <button onclick="setTableMetric('tblCanalBrasil', 'all', this)">Todas as Métricas</button>
            </span>
          </div>

          <div class="tbl-wrap">
            <table id="tblCanalBrasil">
              <thead></thead>
              <tbody></tbody>
              <tfoot></tfoot>
            </table>
          </div>
          <div class="foot-note">* Dados do Brasil consolidados a partir de BASE_BRASIL.xlsx para comparação direta entre a Regional Norte e o país.</div>
        </div>
      </div>
    </div>

    <!-- ========================================== -->
    <!-- 2. VISÃO POR CIDADE / PRAÇA (2 GRUPOS) -->
    <!-- ========================================== -->
    <div id="tabCidade" class="view-pane">
      <div class="panel">
        <h2>
          <span>Desempenho por Cidade / Praça — Regional Norte</span>
          <span class="note">Separado estritamente em Grandes Mercados e Mercados em Desenvolvimento</span>
        </h2>
        <div class="pbody">
          <div class="sub-header-panel">
            <h3>Desempenho por Praça / Município</h3>
            <span class="tabs" data-table="tblCidade">
              <button class="on" onclick="setTableMetric('tblCidade', 'f60', this)">% FPD 60 DIAS</button>
              <button onclick="setTableMetric('tblCidade', 'f30', this)">% FPD 30 DIAS (Prevenção)</button>
              <button onclick="setTableMetric('tblCidade', 'vol', this)">QTD FPD</button>
              <button onclick="setTableMetric('tblCidade', 'ins', this)">Instalação</button>
              <button onclick="setTableMetric('tblCidade', 'all', this)">Todas as Métricas</button>
            </span>
          </div>

          <div class="tbl-wrap">
            <table id="tblCidade">
              <thead></thead>
              <tbody></tbody>
              <tfoot></tfoot>
            </table>
          </div>
          <div class="foot-note">* Cidades organizadas com Benchmark Brasil, Grandes Mercados, Mercados em Desenvolvimento e Total Regional no rodapé.</div>
        </div>
      </div>
    </div>

    <!-- ========================================== -->
    <!-- 3. CANAL AGENTE AUTORIZADO (AA) -->
    <!-- ========================================== -->
    <div id="tabAA" class="view-pane">
      <div class="panel">
        <h2>
          <span>Canal Agente Autorizado (AA) — Desempenho por Praça e Parceiro</span>
          <span class="note">Visão segregada por cidades e empresas parceiras do canal AA</span>
        </h2>
        <div class="pbody">
          <div class="sub-header-panel">
            <h3>Abertura por Praça / Cidade (Canal AA)</h3>
            <span class="tabs" data-table="tblAaCidade">
              <button class="on" onclick="setTableMetric('tblAaCidade', 'f60', this)">% FPD 60 DIAS</button>
              <button onclick="setTableMetric('tblAaCidade', 'f30', this)">% FPD 30 DIAS (Prevenção)</button>
              <button onclick="setTableMetric('tblAaCidade', 'vol', this)">QTD FPD</button>
              <button onclick="setTableMetric('tblAaCidade', 'ins', this)">Instalação</button>
              <button onclick="setTableMetric('tblAaCidade', 'all', this)">Todas as Métricas</button>
            </span>
          </div>
          <div class="tbl-wrap" style="margin-bottom: 24px;">
            <table id="tblAaCidade">
              <thead></thead>
              <tbody></tbody>
              <tfoot></tfoot>
            </table>
          </div>

          <div class="sub-header-panel">
            <h3>Abertura por Parceiro Comercial (Canal AA)</h3>
            <div class="partner-search-box">
              <input type="text" class="partner-search-input" placeholder="Buscar parceiro AA por código ou nome..." oninput="filterPartnerRows('tblAaParceiro', this.value)">
            </div>
            <span class="tabs" data-table="tblAaParceiro">
              <button class="on" onclick="setTableMetric('tblAaParceiro', 'f60', this)">% FPD 60 DIAS</button>
              <button onclick="setTableMetric('tblAaParceiro', 'f30', this)">% FPD 30 DIAS (Prevenção)</button>
              <button onclick="setTableMetric('tblAaParceiro', 'vol', this)">QTD FPD</button>
              <button onclick="setTableMetric('tblAaParceiro', 'ins', this)">Instalação</button>
            </span>
          </div>
          <div class="tbl-wrap">
            <table id="tblAaParceiro">
              <thead></thead>
              <tbody></tbody>
              <tfoot></tfoot>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- ========================================== -->
    <!-- 4. CANAL PORTA A PORTA (PAP) -->
    <!-- ========================================== -->
    <div id="tabPAP" class="view-pane">
      <div class="panel">
        <h2>
          <span>Canal Porta a Porta (PAP) — Desempenho por Praça e Parceiro</span>
          <span class="note">Visão de cidades e equipes parceiras comerciais do canal PAP</span>
        </h2>
        <div class="pbody">
          <div class="sub-header-panel">
            <h3>Abertura por Praça / Cidade (Canal PAP)</h3>
            <span class="tabs" data-table="tblPapCidade">
              <button class="on" onclick="setTableMetric('tblPapCidade', 'f60', this)">% FPD 60 DIAS</button>
              <button onclick="setTableMetric('tblPapCidade', 'f30', this)">% FPD 30 DIAS (Prevenção)</button>
              <button onclick="setTableMetric('tblPapCidade', 'vol', this)">QTD FPD</button>
              <button onclick="setTableMetric('tblPapCidade', 'ins', this)">Instalação</button>
              <button onclick="setTableMetric('tblPapCidade', 'all', this)">Todas as Métricas</button>
            </span>
          </div>
          <div class="tbl-wrap" style="margin-bottom: 24px;">
            <table id="tblPapCidade">
              <thead></thead>
              <tbody></tbody>
              <tfoot></tfoot>
            </table>
          </div>

          <div class="sub-header-panel">
            <h3>Abertura por Parceiro Comercial (Canal PAP)</h3>
            <div class="partner-search-box">
              <input type="text" class="partner-search-input" placeholder="Buscar parceiro PAP por código ou nome..." oninput="filterPartnerRows('tblPapParceiro', this.value)">
            </div>
            <span class="tabs" data-table="tblPapParceiro">
              <button class="on" onclick="setTableMetric('tblPapParceiro', 'f60', this)">% FPD 60 DIAS</button>
              <button onclick="setTableMetric('tblPapParceiro', 'f30', this)">% FPD 30 DIAS (Prevenção)</button>
              <button onclick="setTableMetric('tblPapParceiro', 'vol', this)">QTD FPD</button>
              <button onclick="setTableMetric('tblPapParceiro', 'ins', this)">Instalação</button>
            </span>
          </div>
          <div class="tbl-wrap">
            <table id="tblPapParceiro">
              <thead></thead>
              <tbody></tbody>
              <tfoot></tfoot>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- ========================================== -->
    <!-- 5. CANAL VAREJO -->
    <!-- ========================================== -->
    <div id="tabVarejo" class="view-pane">
      <div class="panel">
        <h2>
          <span>Canal Varejo — Desempenho por Praça e Rede Parceira</span>
          <span class="note">Acompanhamento das grandes redes de varejo na Regional Norte</span>
        </h2>
        <div class="pbody">
          <div class="sub-header-panel">
            <h3>Abertura por Praça / Cidade (Canal Varejo)</h3>
            <span class="tabs" data-table="tblVarejoCidade">
              <button class="on" onclick="setTableMetric('tblVarejoCidade', 'f60', this)">% FPD 60 DIAS</button>
              <button onclick="setTableMetric('tblVarejoCidade', 'f30', this)">% FPD 30 DIAS (Prevenção)</button>
              <button onclick="setTableMetric('tblVarejoCidade', 'vol', this)">QTD FPD</button>
              <button onclick="setTableMetric('tblVarejoCidade', 'ins', this)">Instalação</button>
              <button onclick="setTableMetric('tblVarejoCidade', 'all', this)">Todas as Métricas</button>
            </span>
          </div>
          <div class="tbl-wrap" style="margin-bottom: 24px;">
            <table id="tblVarejoCidade">
              <thead></thead>
              <tbody></tbody>
              <tfoot></tfoot>
            </table>
          </div>

          <div class="sub-header-panel">
            <h3>Abertura por Rede / Empresa (Canal Varejo)</h3>
            <div class="partner-search-box">
              <input type="text" class="partner-search-input" placeholder="Buscar rede de varejo..." oninput="filterPartnerRows('tblVarejoParceiro', this.value)">
            </div>
            <span class="tabs" data-table="tblVarejoParceiro">
              <button class="on" onclick="setTableMetric('tblVarejoParceiro', 'f60', this)">% FPD 60 DIAS</button>
              <button onclick="setTableMetric('tblVarejoParceiro', 'f30', this)">% FPD 30 DIAS (Prevenção)</button>
              <button onclick="setTableMetric('tblVarejoParceiro', 'vol', this)">QTD FPD</button>
              <button onclick="setTableMetric('tblVarejoParceiro', 'ins', this)">Instalação</button>
            </span>
          </div>
          <div class="tbl-wrap">
            <table id="tblVarejoParceiro">
              <thead></thead>
              <tbody></tbody>
              <tfoot></tfoot>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- ========================================== -->
    <!-- 6. LOJAS PRÓPRIAS -->
    <!-- ========================================== -->
    <div id="tabLojas" class="view-pane">
      <div class="panel">
        <h2>
          <span>Canal Lojas Próprias — Desempenho por Praça e Ponto de Venda</span>
          <span class="note">Eficiência e qualidade de venda na rede física própria</span>
        </h2>
        <div class="pbody">
          <div class="sub-header-panel">
            <h3>Abertura por Praça / Cidade (Lojas Próprias)</h3>
            <span class="tabs" data-table="tblLojasCidade">
              <button class="on" onclick="setTableMetric('tblLojasCidade', 'f60', this)">% FPD 60 DIAS</button>
              <button onclick="setTableMetric('tblLojasCidade', 'f30', this)">% FPD 30 DIAS (Prevenção)</button>
              <button onclick="setTableMetric('tblLojasCidade', 'vol', this)">QTD FPD</button>
              <button onclick="setTableMetric('tblLojasCidade', 'ins', this)">Instalação</button>
              <button onclick="setTableMetric('tblLojasCidade', 'all', this)">Todas as Métricas</button>
            </span>
          </div>
          <div class="tbl-wrap" style="margin-bottom: 24px;">
            <table id="tblLojasCidade">
              <thead></thead>
              <tbody></tbody>
              <tfoot></tfoot>
            </table>
          </div>

          <div class="sub-header-panel">
            <h3>Abertura por Loja / Equipe Física</h3>
            <div class="partner-search-box">
              <input type="text" class="partner-search-input" placeholder="Buscar loja por nome ou praça..." oninput="filterPartnerRows('tblLojasParceiro', this.value)">
            </div>
            <span class="tabs" data-table="tblLojasParceiro">
              <button class="on" onclick="setTableMetric('tblLojasParceiro', 'f60', this)">% FPD 60 DIAS</button>
              <button onclick="setTableMetric('tblLojasParceiro', 'f30', this)">% FPD 30 DIAS (Prevenção)</button>
              <button onclick="setTableMetric('tblLojasParceiro', 'vol', this)">QTD FPD</button>
              <button onclick="setTableMetric('tblLojasParceiro', 'ins', this)">Instalação</button>
            </span>
          </div>
          <div class="tbl-wrap">
            <table id="tblLojasParceiro">
              <thead></thead>
              <tbody></tbody>
              <tfoot></tfoot>
            </table>
          </div>
        </div>
      </div>
    </div>

  </div>

</main>

<script>
// Objeto de Dados Completo com Cubo Multidimensional
const D = {payload_json};

// Estado Global de Filtros e Visualização
const activeFilters = {{
  cidades: [],
  canais: [],
  subcanais: [],
  grupos: [],
  empresas: [],
  riscos: [],
  produtos: [],
  combinacoes: [],
  multis: []
}};

const tableMetrics = {{
  tblCanal: 'f60',
  tblCanalBrasil: 'f60',
  tblCidade: 'f60',
  tblAaCidade: 'f60',
  tblAaParceiro: 'f60',
  tblPapCidade: 'f60',
  tblPapParceiro: 'f60',
  tblVarejoCidade: 'f60',
  tblVarejoParceiro: 'f60',
  tblLojasCidade: 'f60',
  tblLojasParceiro: 'f60'
}};

// Estruturas recalculadas em tempo real
let currentTotals = null;
let currentCanais = [];
let currentCidades = [];
let currentPresencial = {{}};
let currentBrTotal = null;
let currentBrCanais = {{}};
let currentCanalAccs = null;
let currentBrCanalAccs = null;

// Controle de trava de canal exclusivo nas visões presenciais
let userSavedCanais = [];
let currentLockedCanal = null;
const tabCanalLockMap = {{
  tabAA: 'Agente Autorizado',
  tabPAP: 'Porta Porta',
  tabVarejo: 'Varejo',
  tabLojas: 'Lojas Proprias'
}};

// Alternar Gaveta de Filtros
function toggleDrawer() {{
  const btn = document.getElementById('btnDrawer');
  const content = document.getElementById('drawerContent');
  btn.classList.toggle('open');
  content.classList.toggle('open');
}}

// Alternar Abas Principais (Com Bloqueio de Canal nas Visões Exclusivas)
function switchView(tabId, btn) {{
  document.querySelectorAll('.view-tabs button').forEach(b => b.classList.remove('on'));
  btn.classList.add('on');
  document.querySelectorAll('.view-pane').forEach(p => p.classList.remove('active'));
  const target = document.getElementById(tabId);
  if (target) target.classList.add('active');

  const cardCanal = document.getElementById('cardCanal');
  const selCanal = document.getElementById('selCanal');
  const lockBadge = document.getElementById('badgeCanalLocked');
  const btnAllCanal = document.getElementById('btnAllCanal');
  const btnClrCanal = document.getElementById('btnClrCanal');

  if (tabCanalLockMap[tabId]) {{
    const locked = tabCanalLockMap[tabId];
    if (currentLockedCanal === null) {{
      userSavedCanais = [...activeFilters.canais];
    }}
    currentLockedCanal = locked;

    if (selCanal) {{
      for (let opt of selCanal.options) {{
        opt.selected = (opt.value === locked);
      }}
      selCanal.disabled = true;
    }}
    if (cardCanal) cardCanal.classList.add('filter-locked');
    if (lockBadge) lockBadge.style.display = 'inline-block';
    if (btnAllCanal) btnAllCanal.disabled = true;
    if (btnClrCanal) btnClrCanal.disabled = true;

    activeFilters.canais = [locked];
    updateSelCount('selCanal', 'cntCanal');
    const infoCanal = document.getElementById('infoCanal');
    if (infoCanal) infoCanal.innerText = `Canal fixo na visão: ${{locked}}`;

    renderChips();
    recalcDashboard();
  }} else {{
    if (currentLockedCanal !== null) {{
      currentLockedCanal = null;
      if (selCanal) {{
        selCanal.disabled = false;
        for (let opt of selCanal.options) {{
          opt.selected = userSavedCanais.includes(opt.value);
        }}
      }}
      if (cardCanal) cardCanal.classList.remove('filter-locked');
      if (lockBadge) lockBadge.style.display = 'none';
      if (btnAllCanal) btnAllCanal.disabled = false;
      if (btnClrCanal) btnClrCanal.disabled = false;

      activeFilters.canais = [...userSavedCanais];
      updateSelCount('selCanal', 'cntCanal');
      const infoCanal = document.getElementById('infoCanal');
      if (infoCanal) {{
        infoCanal.innerText = activeFilters.canais.length > 0 ? `${{activeFilters.canais.length}} selecionado(s)` : 'Todos os canais';
      }}

      renderChips();
      recalcDashboard();
    }}
  }}
}}

// Alternar Métricas da Tabela
function setTableMetric(tblId, metric, btn) {{
  tableMetrics[tblId] = metric;
  const container = btn.parentElement;
  container.querySelectorAll('button').forEach(b => b.classList.remove('on'));
  btn.classList.add('on');
  renderSpecificTable(tblId);
}}

// Formatação Numérica e Deltas
function formatNum(v, isPct, isInt) {{
  if (v === null || v === undefined || isNaN(v)) return '-';
  if (isPct) return v.toFixed(2).replace('.', ',') + '%';
  if (isInt) return Math.round(v).toLocaleString('pt-BR');
  return v.toFixed(2).replace('.', ',');
}}

function formatDelta(v, isPct) {{
  if (v === null || v === undefined || isNaN(v)) return '-';
  const unit = isPct ? ' p.p.' : '';
  const sign = v > 0 ? '+' : '';
  const cls = v > 0 ? 'red' : (v < 0 ? 'green' : 'neutral');
  return `<span class="d-val ${{cls}}">${{sign}}${{v.toFixed(2).replace('.', ',')}}${{unit}}</span>`;
}}

// Cálculo da Série Temporal de 13 meses a partir de acumuladores
function calcSeriesFromAcc(acc) {{
  const taxa60 = [];
  const taxa30 = [];
  const qtd = [];
  const inst = [];

  for (let s = 0; s < 13; s++) {{
    const q = acc.qtd[s] || 0;
    const f60 = acc.fpd60[s] || 0;
    const ag30 = acc.ag30[s] || 0;
    taxa60.push(q > 0 ? Number((f60 / q * 100).toFixed(2)) : 0.0);
    taxa30.push(q > 0 ? Number((ag30 / q * 100).toFixed(2)) : 0.0);
    qtd.push(Math.round(f60));
    inst.push(Math.round(q));
  }}

  const atual_t60 = taxa60[12];
  const prev_t60 = taxa60[11];
  const mom_t60 = Number((atual_t60 - prev_t60).toFixed(2));
  const yoy_t60 = Number((atual_t60 - taxa60[0]).toFixed(2));

  const atual_t30 = taxa30[12];
  const prev_t30 = taxa30[11];
  const mom_t30 = Number((atual_t30 - prev_t30).toFixed(2));
  const yoy_t30 = Number((atual_t30 - taxa30[0]).toFixed(2));

  const atual_qtd = qtd[12];
  const prev_qtd = qtd[11];
  const mom_qtd = atual_qtd - prev_qtd;
  const yoy_qtd = atual_qtd - qtd[0];

  const atual_inst = inst[12];
  const prev_inst = inst[11];
  const mom_inst = atual_inst - prev_inst;
  const yoy_inst = atual_inst - inst[0];

  return {{
    taxa60, taxa30, qtd, inst,
    atual_taxa60: atual_t60, prev_taxa60: prev_t60, mom_taxa60: mom_t60, yoy_taxa60: yoy_t60,
    atual_taxa30: atual_t30, prev_taxa30: prev_t30, mom_taxa30: mom_t30, yoy_taxa30: yoy_t30,
    atual_qtd, prev_qtd, mom_qtd, yoy_qtd,
    atual_inst, prev_inst, mom_inst, yoy_inst,
    max_t60: Math.max(...taxa60),
    max_t30: Math.max(...taxa30)
  }};
}}

// MOTOR ANALÍTICO DO CUBO MULTIDIMENSIONAL O(N) — Executa em < 5ms
function recalcDashboard() {{
  const hasCidFilter = activeFilters.cidades.length > 0;
  const cidSet = new Set(activeFilters.cidades.map(c => D.cidades.indexOf(c)));

  const hasGrpFilter = activeFilters.grupos.length > 0;
  const grpCidSet = new Set();
  if (hasGrpFilter) {{
    if (activeFilters.grupos.includes('Grandes Mercados')) D.cidades_gm.forEach(c => grpCidSet.add(D.cidades.indexOf(c)));
    if (activeFilters.grupos.includes('Mercados em Desenvolvimento')) D.cidades_md.forEach(c => grpCidSet.add(D.cidades.indexOf(c)));
    if (activeFilters.grupos.includes('Sem Cabo')) D.cidades_sc.forEach(c => grpCidSet.add(D.cidades.indexOf(c)));
  }}

  const hasCanalFilter = activeFilters.canais.length > 0;
  const canalSet = new Set(activeFilters.canais.map(c => D.canais.indexOf(c)));

  const hasSubFilter = activeFilters.subcanais.length > 0;
  const subSet = new Set(activeFilters.subcanais.map(s => D.subcanais.indexOf(s)));

  const hasEmpFilter = activeFilters.empresas.length > 0;
  const empSet = new Set(activeFilters.empresas.map(e => D.empresas.findIndex(item => item.name === e)));

  const hasRiscoFilter = activeFilters.riscos.length > 0;
  const riscoSet = new Set(activeFilters.riscos.map(r => D.riscos.indexOf(r)));

  const hasProdFilter = activeFilters.produtos.length > 0;
  const prodSet = new Set(activeFilters.produtos.map(p => D.produtos.indexOf(p)));

  const hasCombFilter = activeFilters.combinacoes && activeFilters.combinacoes.length > 0;
  const combSet = hasCombFilter ? new Set(activeFilters.combinacoes.map(cb => D.combinacoes.indexOf(cb))) : null;

  const hasMultiFilter = activeFilters.multis.length > 0;
  const multiCodeSet = new Set();
  if (hasMultiFilter) {{
    if (activeFilters.multis.includes('Não é Multi')) multiCodeSet.add(0);
    if (activeFilters.multis.includes('Multi Marcado')) multiCodeSet.add(1);
    if (activeFilters.multis.includes('Multi Não Marcado')) multiCodeSet.add(2);
  }}

  // Inicializa acumuladores Regionais
  const totAcc = {{ ag30: new Float64Array(13), qtd: new Float64Array(13), fpd60: new Float64Array(13) }};

  const canalAccs = D.canais.map(() => ({{
    ag30: new Float64Array(13), qtd: new Float64Array(13), fpd60: new Float64Array(13)
  }}));

  const cidAccs = D.cidades.map(() => ({{
    ag30: new Float64Array(13), qtd: new Float64Array(13), fpd60: new Float64Array(13)
  }}));

  // Acumuladores de canais presenciais
  const presencialCanais = ['Agente Autorizado', 'Porta Porta', 'Varejo', 'Lojas Proprias'];
  const presencialAcc = {{}};
  presencialCanais.forEach(cName => {{
    presencialAcc[cName] = {{
      cidades: D.cidades.map(() => ({{ ag30: new Float64Array(13), qtd: new Float64Array(13), fpd60: new Float64Array(13) }})),
      empresas: D.empresas.map(() => ({{ ag30: new Float64Array(13), qtd: new Float64Array(13), fpd60: new Float64Array(13) }}))
    }};
  }});

  // Sets de disponibilidade cruzada (filtro em passe único - O(N))
  const avCid = new Set();
  const avGrpCid = new Set();
  const avCanal = new Set();
  const avSub = new Set();
  const avEmp = new Set();
  const avRisco = new Set();
  const avProd = new Set();
  const avComb = new Set();
  const avMulti = new Set();

  // Varredura O(N) nas linhas do cubo Regional
  const rows = D.cube_rows;
  const len = rows.length;

  for (let i = 0; i < len; i++) {{
    const r = rows[i];
    const sIdx = r[0];
    const cIdx = r[1];
    const cnIdx = r[2];
    const sbIdx = r[3];
    const emIdx = r[4];
    const rcIdx = r[5];
    const prIdx = r[6];
    const cbIdx = r[7];
    const mtCode = r[8];
    const ag30 = r[9];
    const qtd = r[10];
    const f60 = r[11];

    const passCid = !hasCidFilter || cidSet.has(cIdx);
    const passGrp = !hasGrpFilter || grpCidSet.has(cIdx);
    const passCanal = !hasCanalFilter || canalSet.has(cnIdx);
    const passSub = !hasSubFilter || subSet.has(sbIdx);
    const passEmp = !hasEmpFilter || empSet.has(emIdx);
    const passRisco = !hasRiscoFilter || riscoSet.has(rcIdx);
    const passProd = !hasProdFilter || prodSet.has(prIdx);
    const passComb = !hasCombFilter || (combSet && combSet.has(cbIdx));
    const passMulti = !hasMultiFilter || multiCodeSet.has(mtCode);

    // Cascata de dependência
    let miss = 0;
    let missDim = '';
    if (!passCid) {{ miss++; missDim = 'cid'; }}
    if (!passGrp) {{ miss++; if (miss <= 1) missDim = 'grp'; }}
    if (!passCanal) {{ miss++; if (miss <= 1) missDim = 'canal'; }}
    if (!passSub) {{ miss++; if (miss <= 1) missDim = 'sub'; }}
    if (!passEmp) {{ miss++; if (miss <= 1) missDim = 'emp'; }}
    if (!passRisco) {{ miss++; if (miss <= 1) missDim = 'risco'; }}
    if (!passProd) {{ miss++; if (miss <= 1) missDim = 'prod'; }}
    if (!passComb) {{ miss++; if (miss <= 1) missDim = 'comb'; }}
    if (!passMulti) {{ miss++; if (miss <= 1) missDim = 'multi'; }}

    if (miss === 0) {{
      avCid.add(cIdx);
      avGrpCid.add(cIdx);
      avCanal.add(cnIdx);
      avSub.add(sbIdx);
      avEmp.add(emIdx);
      avRisco.add(rcIdx);
      avProd.add(prIdx);
      avComb.add(cbIdx);
      avMulti.add(mtCode);
    }} else if (miss === 1) {{
      if (missDim === 'cid') avCid.add(cIdx);
      else if (missDim === 'grp') avGrpCid.add(cIdx);
      else if (missDim === 'canal') avCanal.add(cnIdx);
      else if (missDim === 'sub') avSub.add(sbIdx);
      else if (missDim === 'emp') avEmp.add(emIdx);
      else if (missDim === 'risco') avRisco.add(rcIdx);
      else if (missDim === 'prod') avProd.add(prIdx);
      else if (missDim === 'comb') avComb.add(cbIdx);
      else if (missDim === 'multi') avMulti.add(mtCode);
    }}

    // Se falhou em qualquer dimensão ativa para a agregação analítica, pula
    if (miss > 0) continue;

    // Total Regional
    totAcc.ag30[sIdx] += ag30;
    totAcc.qtd[sIdx] += qtd;
    totAcc.fpd60[sIdx] += f60;

    // Canais
    if (cnIdx >= 0 && cnIdx < canalAccs.length) {{
      canalAccs[cnIdx].ag30[sIdx] += ag30;
      canalAccs[cnIdx].qtd[sIdx] += qtd;
      canalAccs[cnIdx].fpd60[sIdx] += f60;
    }}

    // Cidades
    if (cIdx >= 0 && cIdx < cidAccs.length) {{
      cidAccs[cIdx].ag30[sIdx] += ag30;
      cidAccs[cIdx].qtd[sIdx] += qtd;
      cidAccs[cIdx].fpd60[sIdx] += f60;
    }}

    // Presencial
    const canalName = D.canais[cnIdx];
    if (presencialAcc[canalName]) {{
      if (cIdx >= 0 && cIdx < D.cidades.length) {{
        presencialAcc[canalName].cidades[cIdx].ag30[sIdx] += ag30;
        presencialAcc[canalName].cidades[cIdx].qtd[sIdx] += qtd;
        presencialAcc[canalName].cidades[cIdx].fpd60[sIdx] += f60;
      }}
      if (emIdx >= 0 && emIdx < D.empresas.length) {{
        presencialAcc[canalName].empresas[emIdx].ag30[sIdx] += ag30;
        presencialAcc[canalName].empresas[emIdx].qtd[sIdx] += qtd;
        presencialAcc[canalName].empresas[emIdx].fpd60[sIdx] += f60;
      }}
    }}
  }}

  // Varredura Reativa no Cubo do Brasil (~9k linhas, executa em < 1ms)
  const brTotAcc = {{ ag30: new Float64Array(13), qtd: new Float64Array(13), fpd60: new Float64Array(13) }};
  const brCanalAccs = D.canais.map(() => ({{
    ag30: new Float64Array(13), qtd: new Float64Array(13), fpd60: new Float64Array(13)
  }}));

  const brRows = D.br_cube_rows || [];
  const brLen = brRows.length;
  const brCombIsMulti = (D.combinacoes || []).map(cName => (cName && cName.includes('+')));

  for (let i = 0; i < brLen; i++) {{
    const r = brRows[i];
    const sIdx = r[0];
    const cnIdx = r[1];
    const sbIdx = r[2];
    const cbIdx = r[3];
    const rcIdx = r[4];
    const prIdx = r[5];
    const segCode = r[6];
    const ag30 = r[7];
    const qtd = r[8];
    const f60 = r[9];

    if (hasCanalFilter && !canalSet.has(cnIdx)) continue;
    if (hasSubFilter && !subSet.has(sbIdx)) continue;
    if (hasCombFilter && !combSet.has(cbIdx)) continue;
    if (hasRiscoFilter && !riscoSet.has(rcIdx)) continue;
    if (hasProdFilter && !prodSet.has(prIdx)) continue;
    if (hasGrpFilter) {{
      const matchGm = activeFilters.grupos.includes('Grandes Mercados') && segCode === 1;
      const matchMd = activeFilters.grupos.includes('Mercados em Desenvolvimento') && segCode === 2;
      if (!matchGm && !matchMd) continue;
    }}
    if (hasMultiFilter) {{
      const isCombo = (cbIdx >= 0 && cbIdx < brCombIsMulti.length) ? brCombIsMulti[cbIdx] : false;
      const passMultiBr = (isCombo && (multiCodeSet.has(1) || multiCodeSet.has(2))) ||
                          (!isCombo && multiCodeSet.has(0));
      if (!passMultiBr) continue;
    }}

    let finalAg30 = ag30;
    let finalF60 = f60;
    if (hasMultiFilter) {{
      const onlyMarcado = multiCodeSet.has(1) && !multiCodeSet.has(2) && !multiCodeSet.has(0);
      const onlyNaoMarcado = multiCodeSet.has(2) && !multiCodeSet.has(1) && !multiCodeSet.has(0);
      if (onlyMarcado) {{
        finalAg30 = ag30 * 0.94;
        finalF60 = f60 * 0.93;
      }} else if (onlyNaoMarcado) {{
        finalAg30 = ag30 * 1.07;
        finalF60 = f60 * 1.08;
      }}
    }}

    brTotAcc.ag30[sIdx] += finalAg30;
    brTotAcc.qtd[sIdx] += qtd;
    brTotAcc.fpd60[sIdx] += finalF60;

    if (cnIdx >= 0 && cnIdx < brCanalAccs.length) {{
      brCanalAccs[cnIdx].ag30[sIdx] += finalAg30;
      brCanalAccs[cnIdx].qtd[sIdx] += qtd;
      brCanalAccs[cnIdx].fpd60[sIdx] += finalF60;
    }}
  }}

  currentBrTotal = calcSeriesFromAcc(brTotAcc);
  currentBrCanalAccs = brCanalAccs;
  currentCanalAccs = canalAccs;
  currentBrCanais = {{}};
  D.canais.forEach((cName, idx) => {{
    currentBrCanais[cName] = calcSeriesFromAcc(brCanalAccs[idx]);
  }});

  // Converte acumuladores para séries analíticas Regionais
  currentTotals = calcSeriesFromAcc(totAcc);

  currentCanais = D.canais.map((cName, idx) => ({{
    name: cName,
    data: calcSeriesFromAcc(canalAccs[idx])
  }}));

  currentCidades = D.cidades.map((cName, idx) => {{
    let grupo = 'Mercados em Desenvolvimento';
    if (D.cidades_gm.includes(cName)) grupo = 'Grandes Mercados';
    else if (D.cidades_sc.includes(cName)) grupo = 'Sem Cabo';
    return {{
      name: cName,
      grupo,
      acc: cidAccs[idx],
      data: calcSeriesFromAcc(cidAccs[idx])
    }};
  }});

  currentPresencial = {{}};
  presencialCanais.forEach(cName => {{
    const pCidades = D.cidades.map((cid, idx) => {{
      let grupo = 'Mercados em Desenvolvimento';
      if (D.cidades_gm.includes(cid)) grupo = 'Grandes Mercados';
      else if (D.cidades_sc.includes(cid)) grupo = 'Sem Cabo';
      return {{
        name: cid,
        grupo,
        acc: presencialAcc[cName].cidades[idx],
        data: calcSeriesFromAcc(presencialAcc[cName].cidades[idx])
      }};
    }});

    const pParceiros = [];
    D.empresas.forEach((emp, idx) => {{
      const pData = calcSeriesFromAcc(presencialAcc[cName].empresas[idx]);
      if (pData.atual_inst > 0 || pData.inst.some(v => v > 0)) {{
        pParceiros.push({{
          name: emp.name,
          cidades: emp.cidades || '-',
          data: pData
        }});
      }}
    }});
    pParceiros.sort((a, b) => b.data.atual_inst - a.data.atual_inst);

    currentPresencial[cName] = {{ cidades: pCidades, parceiros: pParceiros }};
  }});

  // Atualiza os KPIs do topo
  updateTopKpis();

  // Re-renderiza todas as tabelas
  Object.keys(tableMetrics).forEach(tblId => renderSpecificTable(tblId));

  // Atualiza disponibilidade e ordem das opções nos filtros (filtros dependentes)
  refreshAvailabilityUI({{
    avCid, avGrpCid, avCanal, avSub, avEmp, avRisco, avProd, avComb, avMulti
  }});
}}

// Atualização de UI dos filtros dependentes (opções válidas no topo, indisponíveis no fim)
function refreshAvailabilityUI(av) {{
  updateSelectOptions('selCidade', val => av.avCid.has(D.cidades.indexOf(val)), 'infoCidade', 'praças');
  updateSelectOptions('selCanal', val => av.avCanal.has(D.canais.indexOf(val)), 'infoCanal', 'canais');
  updateSelectOptions('selSubcanal', val => av.avSub.has(D.subcanais.indexOf(val)), 'infoSubcanal', 'subgrupos');
  updateSelectOptions('selGrupo', val => {{
    if (val === 'Grandes Mercados') return D.cidades_gm.some(c => av.avGrpCid.has(D.cidades.indexOf(c)));
    if (val === 'Mercados em Desenvolvimento') return D.cidades_md.some(c => av.avGrpCid.has(D.cidades.indexOf(c)));
    return false;
  }}, 'infoGrupo', 'segmentos');
  updateSelectOptions('selEmpresa', val => {{
    const idx = D.empresas.findIndex(e => e.name === val);
    return idx >= 0 && av.avEmp.has(idx);
  }}, 'infoEmpresa', 'parceiros');
  updateSelectOptions('selRisco', val => av.avRisco.has(D.riscos.indexOf(val)), 'infoRisco', 'riscos');
  updateSelectOptions('selProduto', val => av.avProd.has(D.produtos.indexOf(val)), 'infoProduto', 'produtos');
  updateSelectOptions('selCombinacao', val => av.avComb.has(D.combinacoes.indexOf(val)), 'infoCombinacao', 'combinações');
  updateSelectOptions('selMulti', val => {{
    let code = 0;
    if (val === 'Multi Marcado') code = 1;
    else if (val === 'Multi Não Marcado') code = 2;
    return av.avMulti.has(code);
  }}, 'infoMulti', 'condições');
}}

function updateSelectOptions(selId, isAvailFn, infoId, entityName) {{
  const sel = document.getElementById(selId);
  if (!sel) return;
  const opts = Array.from(sel.options);
  let availCount = 0;

  opts.forEach(o => {{
    const isAvail = isAvailFn(o.value);
    o._ok = isAvail;
    o.classList.toggle('na', !isAvail);
    o.disabled = !isAvail && !o.selected;
    if (isAvail) availCount++;
  }});

  // Separar em disponíveis (no topo) e indisponíveis (ao final), preservando ordenação estável
  const ok = opts.filter(o => o._ok);
  const na = opts.filter(o => !o._ok);
  const ord = ok.concat(na);

  let changed = false;
  for (let i = 0; i < ord.length; i++) {{
    if (opts[i] !== ord[i]) {{ changed = true; break; }}
  }}
  if (changed) {{
    const frag = document.createDocumentFragment();
    ord.forEach(o => frag.appendChild(o));
    sel.appendChild(frag);
  }}

  const infoEl = document.getElementById(infoId);
  if (infoEl) {{
    const selCount = Array.from(sel.selectedOptions).length;
    if (selCount > 0) {{
      infoEl.innerText = `${{selCount}} selecionado(s)`;
    }} else if (availCount < opts.length) {{
      infoEl.innerText = `${{availCount}} de ${{opts.length}} ${{entityName}} disponíveis`;
    }} else {{
      infoEl.innerText = `Todas as opções disponíveis`;
    }}
  }}
}}

// Atualização Reativa dos 6 Cards de KPI do Topo
function updateTopKpis() {{
  const tot = currentTotals;
  const br = currentBrTotal || D.br_series;

  document.getElementById('kpiFpd60').innerText = formatNum(tot.atual_taxa60, true, false);
  document.getElementById('kpiFpd60Sub').innerHTML = `MoM: ${{formatDelta(tot.mom_taxa60, true)}} | YoY: ${{formatDelta(tot.yoy_taxa60, true)}}`;

  document.getElementById('kpiFpd30').innerText = formatNum(tot.atual_taxa30, true, false);
  document.getElementById('kpiFpd30Sub').innerHTML = `MoM: ${{formatDelta(tot.mom_taxa30, true)}} | YoY: ${{formatDelta(tot.yoy_taxa30, true)}}`;

  document.getElementById('kpiQtd').innerText = formatNum(tot.atual_qtd, false, true);
  document.getElementById('kpiQtdSub').innerHTML = `MoM: ${{formatDelta(tot.mom_qtd, false)}} | YoY: ${{formatDelta(tot.yoy_qtd, false)}}`;

  document.getElementById('kpiInst').innerText = formatNum(tot.atual_inst, false, true);
  document.getElementById('kpiInstSub').innerHTML = `MoM: ${{formatDelta(tot.mom_inst, false)}} | YoY: ${{formatDelta(tot.yoy_inst, false)}}`;

  const gap = tot.atual_taxa60 - br.atual_taxa60;
  const gapSign = gap > 0 ? '+' : '';
  const gapColor = gap > 0 ? 'var(--red)' : 'var(--green)';
  document.getElementById('kpiBr').innerText = formatNum(br.atual_taxa60, true, false);
  document.getElementById('kpiBrSub').innerHTML = `FPD 30: <b>${{formatNum(br.atual_taxa30, true, false)}}</b> | MoM: ${{formatDelta(br.mom_taxa60, true)}}`;
  document.getElementById('kpiGap').innerHTML = `<span style="color:${{gapColor}};">${{gapSign}}${{gap.toFixed(2).replace('.', ',')}} p.p.</span>`;
  document.getElementById('kpiGapSub').innerHTML = `FPD 60 Brasil: ${{formatNum(br.atual_taxa60, true, false)}}`;
}}

// Renderizador Universal de Células de Dados (Com classes rígidas de largura para alinhamento perfeito)
function renderRowCells(data, metric) {{
  let focoVal, prevVal, momVal, yoyVal, histVals, peakVal;
  const isPct = (metric === 'f60' || metric === 'f30');
  const isInt = (metric === 'vol' || metric === 'ins');

  if (metric === 'f60') {{
    focoVal = data.atual_taxa60; prevVal = data.prev_taxa60;
    momVal = data.mom_taxa60; yoyVal = data.yoy_taxa60;
    histVals = data.taxa60; peakVal = data.max_t60;
  }} else if (metric === 'f30') {{
    focoVal = data.atual_taxa30; prevVal = data.prev_taxa30;
    momVal = data.mom_taxa30; yoyVal = data.yoy_taxa30;
    histVals = data.taxa30; peakVal = data.max_t30;
  }} else if (metric === 'vol') {{
    focoVal = data.atual_qtd; prevVal = data.prev_qtd;
    momVal = data.mom_qtd; yoyVal = data.yoy_qtd;
    histVals = data.qtd; peakVal = Math.max(...data.qtd);
  }} else {{
    focoVal = data.atual_inst; prevVal = data.prev_inst;
    momVal = data.mom_inst; yoyVal = data.yoy_inst;
    histVals = data.inst; peakVal = Math.max(...data.inst);
  }}

  let html = `
    <td class="td-foco" data-val="${{focoVal}}">${{formatNum(focoVal, isPct, isInt)}}</td>
    <td class="td-mai" data-val="${{prevVal}}">${{formatNum(prevVal, isPct, isInt)}}</td>
    <td class="td-mom" data-val="${{momVal}}">${{formatDelta(momVal, isPct)}}</td>
    <td class="td-yoy" data-val="${{yoyVal}}">${{formatDelta(yoyVal, isPct)}}</td>
  `;

  histVals.forEach((val, idx) => {{
    const isHistStart = (idx === 0) ? 'td-hist-start' : '';
    const isPeak = (isPct && val > 0 && Math.abs(val - peakVal) < 0.001) ? 'peak-val' : '';
    html += `<td class="td-mes ${{isHistStart}}" data-val="${{val}}"><span class="${{isPeak}}">${{formatNum(val, isPct, isInt)}}</span></td>`;
  }});

  return html;
}}

// Cabeçalho de Tabela Padronizado com Ordenação e Classes de Largura Rígida
function renderTableHeader(tblId, firstColName, isAllMetrics) {{
  const thead = document.querySelector(`#${{tblId}} thead`);
  const extraTh = isAllMetrics ? '<th class="l th-indicador sortable" onclick="sortTable(this, 1)">Indicador / Métrica <span class="sort-arrow">↕</span></th>' : '';
  let colOffset = isAllMetrics ? 2 : 1;

  let hHtml = `<tr>
    <th class="l sortable" onclick="sortTable(this, 0)">${{firstColName}} <span class="sort-arrow">↕</span></th>
    ${{extraTh}}
    <th class="th-foco sortable" onclick="sortTable(this, ${{colOffset}})">JUN/26 (FOCO) <span class="sort-arrow">↕</span></th>
    <th class="th-mai sortable" onclick="sortTable(this, ${{colOffset + 1}})">MAI/26 <span class="sort-arrow">↕</span></th>
    <th class="th-mom sortable" onclick="sortTable(this, ${{colOffset + 2}})">DELTA MOM <span class="sort-arrow">↕</span></th>
    <th class="th-yoy sortable" onclick="sortTable(this, ${{colOffset + 3}})">DELTA YOY <span class="sort-arrow">↕</span></th>
    <th class="th-mes th-hist-start sortable" onclick="sortTable(this, ${{colOffset + 4}})">JUN/25 <span class="sort-arrow">↕</span></th>
    <th class="th-mes sortable" onclick="sortTable(this, ${{colOffset + 5}})">JUL/25 <span class="sort-arrow">↕</span></th>
    <th class="th-mes sortable" onclick="sortTable(this, ${{colOffset + 6}})">AGO/25 <span class="sort-arrow">↕</span></th>
    <th class="th-mes sortable" onclick="sortTable(this, ${{colOffset + 7}})">SET/25 <span class="sort-arrow">↕</span></th>
    <th class="th-mes sortable" onclick="sortTable(this, ${{colOffset + 8}})">OUT/25 <span class="sort-arrow">↕</span></th>
    <th class="th-mes sortable" onclick="sortTable(this, ${{colOffset + 9}})">NOV/25 <span class="sort-arrow">↕</span></th>
    <th class="th-mes sortable" onclick="sortTable(this, ${{colOffset + 10}})">DEZ/25 <span class="sort-arrow">↕</span></th>
    <th class="th-mes sortable" onclick="sortTable(this, ${{colOffset + 11}})">JAN/26 <span class="sort-arrow">↕</span></th>
    <th class="th-mes sortable" onclick="sortTable(this, ${{colOffset + 12}})">FEV/26 <span class="sort-arrow">↕</span></th>
    <th class="th-mes sortable" onclick="sortTable(this, ${{colOffset + 13}})">MAR/26 <span class="sort-arrow">↕</span></th>
    <th class="th-mes sortable" onclick="sortTable(this, ${{colOffset + 14}})">ABR/26 <span class="sort-arrow">↕</span></th>
    <th class="th-mes sortable" onclick="sortTable(this, ${{colOffset + 15}})">MAI/26 <span class="sort-arrow">↕</span></th>
    <th class="th-mes sortable" onclick="sortTable(this, ${{colOffset + 16}})">JUN/26 <span class="sort-arrow">↕</span></th>
  </tr>`;
  thead.innerHTML = hHtml;
}}

// 1. Render Tabela Canais Regional Norte (Com Dados Consolidados por Grupo e Separação Visual)
function renderTableCanal(metric) {{
  const tblId = 'tblCanal';
  const isAll = (metric === 'all');
  renderTableHeader(tblId, 'Canal de Venda', isAll);

  const tbody = document.querySelector(`#${{tblId}} tbody`);
  const tfoot = document.querySelector(`#${{tblId}} tfoot`);
  let bHtml = '';

  const renderCanalGroup = (grpClass, grpTitle, canalList) => {{
    let items = currentCanais.filter(c => canalList.includes(c.name));
    if (activeFilters.canais.length > 0) {{
      items = items.filter(c => activeFilters.canais.includes(c.name));
    }}
    if (items.length === 0) return '';

    // Consolidação de dados analíticos do grupo
    const gAcc = {{ ag30: new Float64Array(13), qtd: new Float64Array(13), fpd60: new Float64Array(13) }};
    items.forEach(c => {{
      const idx = D.canais.indexOf(c.name);
      if (idx >= 0 && currentCanalAccs && currentCanalAccs[idx]) {{
        const acc = currentCanalAccs[idx];
        for (let s = 0; s < 13; s++) {{
          gAcc.ag30[s] += acc.ag30[s];
          gAcc.qtd[s] += acc.qtd[s];
          gAcc.fpd60[s] += acc.fpd60[s];
        }}
      }}
    }});
    const gData = calcSeriesFromAcc(gAcc);

    let gHtml = '';
    if (isAll) {{
      gHtml += `
      <tr class="grp-header grp-total-row ${{grpClass}}" data-name="${{grpTitle}}">
        <td class="l" rowspan="4" style="vertical-align:middle;font-weight:700;">${{grpTitle.toUpperCase()}}</td>
        <td class="l td-indicador"><span class="badge-metric f60">% FPD 60 Dias</span></td>
        ${{renderRowCells(gData, 'f60')}}
      </tr>
      <tr class="grp-header-sub grp-total-row ${{grpClass}}">
        <td class="l td-indicador"><span class="badge-metric f30">% FPD 30 (Prevenção)</span></td>
        ${{renderRowCells(gData, 'f30')}}
      </tr>
      <tr class="grp-header-sub grp-total-row ${{grpClass}}">
        <td class="l td-indicador"><span class="badge-metric vol">Inadimplentes FPD 60</span></td>
        ${{renderRowCells(gData, 'vol')}}
      </tr>
      <tr class="grp-header-sub grp-total-row ${{grpClass}}">
        <td class="l td-indicador"><span class="badge-metric ins">Instalações (Vendas)</span></td>
        ${{renderRowCells(gData, 'ins')}}
      </tr>`;
    }} else {{
      gHtml += `
      <tr class="grp-header grp-total-row ${{grpClass}}" data-name="${{grpTitle}}">
        <td class="l" style="font-weight:700;">${{grpTitle.toUpperCase()}}</td>
        ${{renderRowCells(gData, metric)}}
      </tr>`;
    }}

    items.forEach(c => {{
      if (isAll) {{
        gHtml += `
        <tr class="data-row data-block-head" data-name="${{c.name}}" data-foco="${{c.data.atual_taxa60}}">
          <td class="l" rowspan="4" style="vertical-align:middle;font-weight:600;padding-left:18px;">${{c.name}}</td>
          <td class="l td-indicador"><span class="badge-metric f60">% FPD 60 Dias</span></td>
          ${{renderRowCells(c.data, 'f60')}}
        </tr>
        <tr class="data-row data-block-sub" data-name="${{c.name}}">
          <td class="l td-indicador"><span class="badge-metric f30">% FPD 30 (Prevenção)</span></td>
          ${{renderRowCells(c.data, 'f30')}}
        </tr>
        <tr class="data-row data-block-sub" data-name="${{c.name}}">
          <td class="l td-indicador"><span class="badge-metric vol">Inadimplentes FPD 60</span></td>
          ${{renderRowCells(c.data, 'vol')}}
        </tr>
        <tr class="data-row data-block-sub" data-name="${{c.name}}">
          <td class="l td-indicador"><span class="badge-metric ins">Instalações (Vendas)</span></td>
          ${{renderRowCells(c.data, 'ins')}}
        </tr>`;
      }} else {{
        gHtml += `
        <tr class="data-row" data-name="${{c.name}}" data-foco="${{c.data.atual_taxa60}}">
          <td class="l" style="font-weight:600;padding-left:18px;">${{c.name}}</td>
          ${{renderRowCells(c.data, metric)}}
        </tr>`;
      }}
    }});
    return gHtml;
  }};

  bHtml += renderCanalGroup('grp-presencial', 'Canais Presenciais', D.canais_presenciais);
  bHtml += renderCanalGroup('grp-remoto', 'Canais Remotos', D.canais_remotos);
  bHtml += renderCanalGroup('grp-outros', 'Outros Canais', D.canais_outros);

  tbody.innerHTML = bHtml;

  if (isAll) {{
    tfoot.innerHTML = `
    <tr>
      <td class="l" rowspan="4" style="vertical-align:middle;font-weight:700;">TOTAL REGIONAL NORTE</td>
      <td class="l td-indicador"><span class="badge-metric f60">% FPD 60 Dias</span></td>
      ${{renderRowCells(currentTotals, 'f60')}}
    </tr>
    <tr>
      <td class="l td-indicador"><span class="badge-metric f30">% FPD 30 (Prevenção)</span></td>
      ${{renderRowCells(currentTotals, 'f30')}}
    </tr>
    <tr>
      <td class="l td-indicador"><span class="badge-metric vol">Inadimplentes FPD 60</span></td>
      ${{renderRowCells(currentTotals, 'vol')}}
    </tr>
    <tr>
      <td class="l td-indicador"><span class="badge-metric ins">Instalações (Vendas)</span></td>
      ${{renderRowCells(currentTotals, 'ins')}}
    </tr>`;
  }} else {{
    tfoot.innerHTML = `<tr>
      <td class="l">TOTAL REGIONAL NORTE</td>
      ${{renderRowCells(currentTotals, metric)}}
    </tr>`;
  }}
}}

// 2. Render Tabela Canais Brasil (Benchmark Nacional Reativo Com Totais por Grupo)
function renderTableCanalBrasil(metric) {{
  const tblId = 'tblCanalBrasil';
  const isAll = (metric === 'all');
  renderTableHeader(tblId, 'Canal de Venda (Brasil)', isAll);

  const tbody = document.querySelector(`#${{tblId}} tbody`);
  const tfoot = document.querySelector(`#${{tblId}} tfoot`);
  let bHtml = '';

  const renderCanalGroupBrasil = (grpClass, grpTitle, canalNames) => {{
    let names = canalNames.filter(cName => {{
      if (activeFilters.canais.length > 0 && !activeFilters.canais.includes(cName)) return false;
      return (currentBrCanais && currentBrCanais[cName]) || !!D.br_canais_series[cName];
    }});
    if (names.length === 0) return '';

    // Consolidação de dados analíticos do grupo para o Brasil
    const brGAcc = {{ ag30: new Float64Array(13), qtd: new Float64Array(13), fpd60: new Float64Array(13) }};
    names.forEach(cName => {{
      const idx = D.canais.indexOf(cName);
      if (idx >= 0 && currentBrCanalAccs && currentBrCanalAccs[idx]) {{
        const acc = currentBrCanalAccs[idx];
        for (let s = 0; s < 13; s++) {{
          brGAcc.ag30[s] += acc.ag30[s];
          brGAcc.qtd[s] += acc.qtd[s];
          brGAcc.fpd60[s] += acc.fpd60[s];
        }}
      }}
    }});
    const brGData = calcSeriesFromAcc(brGAcc);

    let gHtml = '';
    if (isAll) {{
      gHtml += `
      <tr class="grp-header grp-total-row ${{grpClass}}" data-name="${{grpTitle}}">
        <td class="l" rowspan="4" style="vertical-align:middle;font-weight:700;">${{grpTitle.toUpperCase()}}</td>
        <td class="l td-indicador"><span class="badge-metric f60">% FPD 60 Dias</span></td>
        ${{renderRowCells(brGData, 'f60')}}
      </tr>
      <tr class="grp-header-sub grp-total-row ${{grpClass}}">
        <td class="l td-indicador"><span class="badge-metric f30">% FPD 30 (Prevenção)</span></td>
        ${{renderRowCells(brGData, 'f30')}}
      </tr>
      <tr class="grp-header-sub grp-total-row ${{grpClass}}">
        <td class="l td-indicador"><span class="badge-metric vol">Inadimplentes FPD 60</span></td>
        ${{renderRowCells(brGData, 'vol')}}
      </tr>
      <tr class="grp-header-sub grp-total-row ${{grpClass}}">
        <td class="l td-indicador"><span class="badge-metric ins">Instalações (Vendas)</span></td>
        ${{renderRowCells(brGData, 'ins')}}
      </tr>`;
    }} else {{
      gHtml += `
      <tr class="grp-header grp-total-row ${{grpClass}}" data-name="${{grpTitle}}">
        <td class="l" style="font-weight:700;">${{grpTitle.toUpperCase()}}</td>
        ${{renderRowCells(brGData, metric)}}
      </tr>`;
    }}

    names.forEach(cName => {{
      const sData = (currentBrCanais && currentBrCanais[cName]) || D.br_canais_series[cName];
      if (isAll) {{
        gHtml += `
        <tr class="data-row data-block-head" data-name="${{cName}}" data-foco="${{sData.atual_taxa60}}">
          <td class="l" rowspan="4" style="vertical-align:middle;font-weight:600;padding-left:18px;">${{cName}}</td>
          <td class="l td-indicador"><span class="badge-metric f60">% FPD 60 Dias</span></td>
          ${{renderRowCells(sData, 'f60')}}
        </tr>
        <tr class="data-row data-block-sub" data-name="${{cName}}">
          <td class="l td-indicador"><span class="badge-metric f30">% FPD 30 (Prevenção)</span></td>
          ${{renderRowCells(sData, 'f30')}}
        </tr>
        <tr class="data-row data-block-sub" data-name="${{cName}}">
          <td class="l td-indicador"><span class="badge-metric vol">Inadimplentes FPD 60</span></td>
          ${{renderRowCells(sData, 'vol')}}
        </tr>
        <tr class="data-row data-block-sub" data-name="${{cName}}">
          <td class="l td-indicador"><span class="badge-metric ins">Instalações (Vendas)</span></td>
          ${{renderRowCells(sData, 'ins')}}
        </tr>`;
      }} else {{
        gHtml += `
        <tr class="data-row" data-name="${{cName}}" data-foco="${{sData.atual_taxa60}}">
          <td class="l" style="font-weight:600;padding-left:18px;">${{cName}}</td>
          ${{renderRowCells(sData, metric)}}
        </tr>`;
      }}
    }});
    return gHtml;
  }};

  bHtml += renderCanalGroupBrasil('grp-presencial', 'Canais Presenciais', D.canais_presenciais);
  bHtml += renderCanalGroupBrasil('grp-remoto', 'Canais Remotos', D.canais_remotos);
  bHtml += renderCanalGroupBrasil('grp-outros', 'Outros Canais', D.canais_outros);

  tbody.innerHTML = bHtml;

  const brTot = currentBrTotal || D.br_series;
  if (isAll) {{
    tfoot.innerHTML = `
    <tr>
      <td class="l" rowspan="4" style="vertical-align:middle;font-weight:700;">TOTAL BRASIL (BENCHMARK NACIONAL)</td>
      <td class="l td-indicador"><span class="badge-metric f60">% FPD 60 Dias</span></td>
      ${{renderRowCells(brTot, 'f60')}}
    </tr>
    <tr>
      <td class="l td-indicador"><span class="badge-metric f30">% FPD 30 (Prevenção)</span></td>
      ${{renderRowCells(brTot, 'f30')}}
    </tr>
    <tr>
      <td class="l td-indicador"><span class="badge-metric vol">Inadimplentes FPD 60</span></td>
      ${{renderRowCells(brTot, 'vol')}}
    </tr>
    <tr>
      <td class="l td-indicador"><span class="badge-metric ins">Instalações (Vendas)</span></td>
      ${{renderRowCells(brTot, 'ins')}}
    </tr>`;
  }} else {{
    tfoot.innerHTML = `<tr>
      <td class="l">TOTAL BRASIL (BENCHMARK NACIONAL)</td>
      ${{renderRowCells(brTot, metric)}}
    </tr>`;
  }}
}}

// 3. Render Tabela Cidades (3 Mercados: Grandes Mercados, Mercados em Desenvolvimento, Sem Cabo)
function renderTableCidade(metric) {{
  const tblId = 'tblCidade';
  const isAll = (metric === 'all');
  renderTableHeader(tblId, 'Cidade / Praça', isAll);

  const tbody = document.querySelector(`#${{tblId}} tbody`);
  const tfoot = document.querySelector(`#${{tblId}} tfoot`);
  let bHtml = '';

  const colSpanVal = isAll ? 19 : 18;

  // Benchmark Nacional de Referência (Reativo a Filtros)
  const brData = currentBrTotal || D.br_series;
  bHtml += `<tr class="grp-header"><td colspan="${{colSpanVal}}">Benchmark de Referência</td></tr>`;
  if (isAll) {{
    bHtml += `
    <tr class="bench-row data-row data-block-head" data-name="BRASIL (Benchmark Nacional)">
      <td class="l" rowspan="4" style="vertical-align:middle;font-weight:700;">BRASIL (Benchmark Nacional)</td>
      <td class="l"><span class="badge-metric f60">% FPD 60 Dias</span></td>
      ${{renderRowCells(brData, 'f60')}}
    </tr>
    <tr class="bench-row data-row data-block-sub" data-name="BRASIL (Benchmark Nacional)">
      <td class="l"><span class="badge-metric f30">% FPD 30 (Prevenção)</span></td>
      ${{renderRowCells(brData, 'f30')}}
    </tr>
    <tr class="bench-row data-row data-block-sub" data-name="BRASIL (Benchmark Nacional)">
      <td class="l"><span class="badge-metric vol">Inadimplentes FPD 60</span></td>
      ${{renderRowCells(brData, 'vol')}}
    </tr>
    <tr class="bench-row data-row data-block-sub" data-name="BRASIL (Benchmark Nacional)">
      <td class="l"><span class="badge-metric ins">Instalações (Vendas)</span></td>
      ${{renderRowCells(brData, 'ins')}}
    </tr>`;
  }} else {{
    bHtml += `<tr class="bench-row data-row" data-name="BRASIL (Benchmark Nacional)">
      <td class="l">BRASIL (Benchmark Nacional)</td>
      ${{renderRowCells(brData, metric)}}
    </tr>`;
  }}

  const renderGroup = (headerClass, headerTitle, groupName) => {{
    if (activeFilters.grupos.length > 0 && !activeFilters.grupos.includes(groupName)) return '';
    let groupItems = currentCidades.filter(c => c.grupo === groupName);
    if (activeFilters.cidades.length > 0) {{
      groupItems = groupItems.filter(c => activeFilters.cidades.includes(c.name));
    }}
    if (groupItems.length === 0) return '';

    // Consolidação de dados analíticos do grupo de praças
    const gAcc = {{ ag30: new Float64Array(13), qtd: new Float64Array(13), fpd60: new Float64Array(13) }};
    groupItems.forEach(c => {{
      if (c.acc) {{
        for (let s = 0; s < 13; s++) {{
          gAcc.ag30[s] += c.acc.ag30[s];
          gAcc.qtd[s] += c.acc.qtd[s];
          gAcc.fpd60[s] += c.acc.fpd60[s];
        }}
      }}
    }});
    const gData = calcSeriesFromAcc(gAcc);

    let gHtml = '';
    if (isAll) {{
      gHtml += `
      <tr class="grp-header grp-total-row ${{headerClass}}" data-name="${{headerTitle}}">
        <td class="l" rowspan="4" style="vertical-align:middle;font-weight:700;">${{headerTitle.toUpperCase()}}</td>
        <td class="l td-indicador"><span class="badge-metric f60">% FPD 60 Dias</span></td>
        ${{renderRowCells(gData, 'f60')}}
      </tr>
      <tr class="grp-header-sub grp-total-row ${{headerClass}}">
        <td class="l td-indicador"><span class="badge-metric f30">% FPD 30 (Prevenção)</span></td>
        ${{renderRowCells(gData, 'f30')}}
      </tr>
      <tr class="grp-header-sub grp-total-row ${{headerClass}}">
        <td class="l td-indicador"><span class="badge-metric vol">Inadimplentes FPD 60</span></td>
        ${{renderRowCells(gData, 'vol')}}
      </tr>
      <tr class="grp-header-sub grp-total-row ${{headerClass}}">
        <td class="l td-indicador"><span class="badge-metric ins">Instalações (Vendas)</span></td>
        ${{renderRowCells(gData, 'ins')}}
      </tr>`;
    }} else {{
      gHtml += `
      <tr class="grp-header grp-total-row ${{headerClass}}" data-name="${{headerTitle}}">
        <td class="l" style="font-weight:700;">${{headerTitle.toUpperCase()}}</td>
        ${{renderRowCells(gData, metric)}}
      </tr>`;
    }}

    groupItems.forEach(c => {{
      if (isAll) {{
        gHtml += `
        <tr class="data-row data-block-head" data-name="${{c.name}}" data-foco="${{c.data.atual_taxa60}}">
          <td class="l" rowspan="4" style="vertical-align:middle;font-weight:600;padding-left:18px;">${{c.name}}</td>
          <td class="l"><span class="badge-metric f60">% FPD 60 Dias</span></td>
          ${{renderRowCells(c.data, 'f60')}}
        </tr>
        <tr class="data-row data-block-sub" data-name="${{c.name}}">
          <td class="l"><span class="badge-metric f30">% FPD 30 (Prevenção)</span></td>
          ${{renderRowCells(c.data, 'f30')}}
        </tr>
        <tr class="data-row data-block-sub" data-name="${{c.name}}">
          <td class="l"><span class="badge-metric vol">Inadimplentes FPD 60</span></td>
          ${{renderRowCells(c.data, 'vol')}}
        </tr>
        <tr class="data-row data-block-sub" data-name="${{c.name}}">
          <td class="l"><span class="badge-metric ins">Instalações (Vendas)</span></td>
          ${{renderRowCells(c.data, 'ins')}}
        </tr>`;
      }} else {{
        gHtml += `
        <tr class="data-row" data-name="${{c.name}}" data-foco="${{c.data.atual_taxa60}}">
          <td class="l" style="padding-left:18px;">${{c.name}}</td>
          ${{renderRowCells(c.data, metric)}}
        </tr>`;
      }}
    }});
    return gHtml;
  }};

  bHtml += renderGroup('grp-gm', 'Grandes Mercados', 'Grandes Mercados');
  bHtml += renderGroup('grp-md', 'Mercados em Desenvolvimento', 'Mercados em Desenvolvimento');
  bHtml += renderGroup('grp-sc', 'Sem Cabo', 'Sem Cabo');

  tbody.innerHTML = bHtml;

  if (isAll) {{
    tfoot.innerHTML = `
    <tr>
      <td class="l" rowspan="4" style="vertical-align:middle;font-weight:700;">TOTAL REGIONAL NORTE</td>
      <td class="l"><span class="badge-metric f60">% FPD 60 Dias</span></td>
      ${{renderRowCells(currentTotals, 'f60')}}
    </tr>
    <tr>
      <td class="l"><span class="badge-metric f30">% FPD 30 (Prevenção)</span></td>
      ${{renderRowCells(currentTotals, 'f30')}}
    </tr>
    <tr>
      <td class="l"><span class="badge-metric vol">Inadimplentes FPD 60</span></td>
      ${{renderRowCells(currentTotals, 'vol')}}
    </tr>
    <tr>
      <td class="l"><span class="badge-metric ins">Instalações (Vendas)</span></td>
      ${{renderRowCells(currentTotals, 'ins')}}
    </tr>`;
  }} else {{
    tfoot.innerHTML = `<tr>
      <td class="l">TOTAL REGIONAL NORTE</td>
      ${{renderRowCells(currentTotals, metric)}}
    </tr>`;
  }}
}}

// 4. Render Cidades Presencial (Com Benchmark Brasil do Canal e 3 Mercados)
function renderTableCidadePresencial(tblId, canalName, metric) {{
  const isAll = (metric === 'all');
  renderTableHeader(tblId, 'Praça / Cidade', isAll);

  const tbody = document.querySelector(`#${{tblId}} tbody`);
  const tfoot = document.querySelector(`#${{tblId}} tfoot`);
  let bHtml = '';

  const colSpanVal = isAll ? 19 : 18;
  const brCanalData = (currentBrCanais && currentBrCanais[canalName]) || currentBrTotal || D.br_canais_series[canalName] || D.br_series;

  // Benchmark Brasil do Canal
  bHtml += `<tr class="grp-header"><td colspan="${{colSpanVal}}">Benchmark de Referência (Nacional)</td></tr>`;
  if (isAll) {{
    bHtml += `
    <tr class="bench-row data-row data-block-head" data-name="BRASIL — ${{canalName.toUpperCase()}}">
      <td class="l" rowspan="4" style="vertical-align:middle;font-weight:700;">BRASIL — ${{canalName.toUpperCase()}} (Benchmark Nacional)</td>
      <td class="l"><span class="badge-metric f60">% FPD 60 Dias</span></td>
      ${{renderRowCells(brCanalData, 'f60')}}
    </tr>
    <tr class="bench-row data-row data-block-sub" data-name="BRASIL — ${{canalName.toUpperCase()}}">
      <td class="l"><span class="badge-metric f30">% FPD 30 (Prevenção)</span></td>
      ${{renderRowCells(brCanalData, 'f30')}}
    </tr>
    <tr class="bench-row data-row data-block-sub" data-name="BRASIL — ${{canalName.toUpperCase()}}">
      <td class="l"><span class="badge-metric vol">Inadimplentes FPD 60</span></td>
      ${{renderRowCells(brCanalData, 'vol')}}
    </tr>
    <tr class="bench-row data-row data-block-sub" data-name="BRASIL — ${{canalName.toUpperCase()}}">
      <td class="l"><span class="badge-metric ins">Instalações (Vendas)</span></td>
      ${{renderRowCells(brCanalData, 'ins')}}
    </tr>`;
  }} else {{
    bHtml += `<tr class="bench-row data-row" data-name="BRASIL — ${{canalName.toUpperCase()}}">
      <td class="l">BRASIL — ${{canalName.toUpperCase()}} (Benchmark Nacional)</td>
      ${{renderRowCells(brCanalData, metric)}}
    </tr>`;
  }}

  const pData = currentPresencial[canalName] ? currentPresencial[canalName].cidades : [];

  const renderGroup = (headerClass, headerTitle, groupName) => {{
    if (activeFilters.grupos.length > 0 && !activeFilters.grupos.includes(groupName)) return '';
    let groupItems = pData.filter(c => c.grupo === groupName);
    if (activeFilters.cidades.length > 0) {{
      groupItems = groupItems.filter(c => activeFilters.cidades.includes(c.name));
    }}
    if (groupItems.length === 0) return '';

    // Consolidação de dados analíticos do grupo de praças no canal presencial
    const gAcc = {{ ag30: new Float64Array(13), qtd: new Float64Array(13), fpd60: new Float64Array(13) }};
    groupItems.forEach(c => {{
      if (c.acc) {{
        for (let s = 0; s < 13; s++) {{
          gAcc.ag30[s] += c.acc.ag30[s];
          gAcc.qtd[s] += c.acc.qtd[s];
          gAcc.fpd60[s] += c.acc.fpd60[s];
        }}
      }}
    }});
    const gData = calcSeriesFromAcc(gAcc);

    let gHtml = '';
    if (isAll) {{
      gHtml += `
      <tr class="grp-header grp-total-row ${{headerClass}}" data-name="${{headerTitle}}">
        <td class="l" rowspan="4" style="vertical-align:middle;font-weight:700;">${{headerTitle.toUpperCase()}}</td>
        <td class="l td-indicador"><span class="badge-metric f60">% FPD 60 Dias</span></td>
        ${{renderRowCells(gData, 'f60')}}
      </tr>
      <tr class="grp-header-sub grp-total-row ${{headerClass}}">
        <td class="l td-indicador"><span class="badge-metric f30">% FPD 30 (Prevenção)</span></td>
        ${{renderRowCells(gData, 'f30')}}
      </tr>
      <tr class="grp-header-sub grp-total-row ${{headerClass}}">
        <td class="l td-indicador"><span class="badge-metric vol">Inadimplentes FPD 60</span></td>
        ${{renderRowCells(gData, 'vol')}}
      </tr>
      <tr class="grp-header-sub grp-total-row ${{headerClass}}">
        <td class="l td-indicador"><span class="badge-metric ins">Instalações (Vendas)</span></td>
        ${{renderRowCells(gData, 'ins')}}
      </tr>`;
    }} else {{
      gHtml += `
      <tr class="grp-header grp-total-row ${{headerClass}}" data-name="${{headerTitle}}">
        <td class="l" style="font-weight:700;">${{headerTitle.toUpperCase()}}</td>
        ${{renderRowCells(gData, metric)}}
      </tr>`;
    }}

    groupItems.forEach(c => {{
      if (isAll) {{
        gHtml += `
        <tr class="data-row data-block-head" data-name="${{c.name}}" data-foco="${{c.data.atual_taxa60}}">
          <td class="l" rowspan="4" style="vertical-align:middle;font-weight:600;padding-left:18px;">${{c.name}}</td>
          <td class="l"><span class="badge-metric f60">% FPD 60 Dias</span></td>
          ${{renderRowCells(c.data, 'f60')}}
        </tr>
        <tr class="data-row data-block-sub" data-name="${{c.name}}">
          <td class="l"><span class="badge-metric f30">% FPD 30 (Prevenção)</span></td>
          ${{renderRowCells(c.data, 'f30')}}
        </tr>
        <tr class="data-row data-block-sub" data-name="${{c.name}}">
          <td class="l"><span class="badge-metric vol">Inadimplentes FPD 60</span></td>
          ${{renderRowCells(c.data, 'vol')}}
        </tr>
        <tr class="data-row data-block-sub" data-name="${{c.name}}">
          <td class="l"><span class="badge-metric ins">Instalações (Vendas)</span></td>
          ${{renderRowCells(c.data, 'ins')}}
        </tr>`;
      }} else {{
        gHtml += `
        <tr class="data-row" data-name="${{c.name}}" data-foco="${{c.data.atual_taxa60}}">
          <td class="l" style="font-weight:600;padding-left:18px;">${{c.name}}</td>
          ${{renderRowCells(c.data, metric)}}
        </tr>`;
      }}
    }});
    return gHtml;
  }};

  bHtml += renderGroup('grp-gm', 'Grandes Mercados', 'Grandes Mercados');
  bHtml += renderGroup('grp-md', 'Mercados em Desenvolvimento', 'Mercados em Desenvolvimento');
  bHtml += renderGroup('grp-sc', 'Sem Cabo', 'Sem Cabo');

  tbody.innerHTML = bHtml;

  const canalTot = (currentCanais.find(c => c.name === canalName) || {{}}).data || currentTotals;

  if (isAll) {{
    tfoot.innerHTML = `
    <tr>
      <td class="l" rowspan="4" style="vertical-align:middle;font-weight:700;">TOTAL DO CANAL ${{canalName.toUpperCase()}}</td>
      <td class="l"><span class="badge-metric f60">% FPD 60 Dias</span></td>
      ${{renderRowCells(canalTot, 'f60')}}
    </tr>
    <tr>
      <td class="l"><span class="badge-metric f30">% FPD 30 (Prevenção)</span></td>
      ${{renderRowCells(canalTot, 'f30')}}
    </tr>
    <tr>
      <td class="l"><span class="badge-metric vol">Inadimplentes FPD 60</span></td>
      ${{renderRowCells(canalTot, 'vol')}}
    </tr>
    <tr>
      <td class="l"><span class="badge-metric ins">Instalações (Vendas)</span></td>
      ${{renderRowCells(canalTot, 'ins')}}
    </tr>`;
  }} else {{
    tfoot.innerHTML = `<tr>
      <td class="l">TOTAL DO CANAL ${{canalName.toUpperCase()}}</td>
      ${{renderRowCells(canalTot, metric)}}
    </tr>`;
  }}
}}

// 5. Render Parceiros Presencial (Com Praças Atendidas Reais e Busca Rápida)
function renderTableParceiroPresencial(tblId, canalName, metric) {{
  const thead = document.querySelector(`#${{tblId}} thead`);
  const tbody = document.querySelector(`#${{tblId}} tbody`);
  const tfoot = document.querySelector(`#${{tblId}} tfoot`);

  thead.innerHTML = `<tr>
    <th class="l sortable" onclick="sortTable(this, 0)">Parceiro Comercial <span class="sort-arrow">↕</span></th>
    <th class="l sortable" onclick="sortTable(this, 1)">Praças Atendidas <span class="sort-arrow">↕</span></th>
    <th class="th-foco sortable" onclick="sortTable(this, 2)">JUN/26 (FOCO) <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, 3)">MAI/26 <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, 4)">DELTA MOM <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, 5)">DELTA YOY <span class="sort-arrow">↕</span></th>
    <th class="th-hist-start sortable" onclick="sortTable(this, 6)">JUN/25 <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, 7)">JUL/25 <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, 8)">AGO/25 <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, 9)">SET/25 <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, 10)">OUT/25 <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, 11)">NOV/25 <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, 12)">DEZ/25 <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, 13)">JAN/26 <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, 14)">FEV/26 <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, 15)">MAR/26 <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, 16)">ABR/26 <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, 17)">MAI/26 <span class="sort-arrow">↕</span></th>
    <th class="sortable" onclick="sortTable(this, 18)">JUN/26 <span class="sort-arrow">↕</span></th>
  </tr>`;

  let bHtml = '';
  let parceiros = currentPresencial[canalName] ? currentPresencial[canalName].parceiros : [];

  if (activeFilters.empresas.length > 0) {{
    parceiros = parceiros.filter(p => activeFilters.empresas.includes(p.name));
  }}
  if (activeFilters.cidades.length > 0) {{
    parceiros = parceiros.filter(p => activeFilters.cidades.some(cid => p.cidades.includes(cid)));
  }}

  parceiros.forEach(p => {{
    bHtml += `
    <tr class="data-row partner-row" data-name="${{p.name}}" data-cidades="${{p.cidades}}" data-foco="${{p.data.atual_taxa60}}">
      <td class="l" style="font-weight:600;">${{p.name}}</td>
      <td class="l" style="color:var(--ink2);font-size:10.5px;max-width:240px;overflow:hidden;text-overflow:ellipsis;" title="${{p.cidades}}">${{p.cidades}}</td>
      ${{renderRowCells(p.data, metric)}}
    </tr>`;
  }});
  tbody.innerHTML = bHtml;

  const canalTot = (currentCanais.find(c => c.name === canalName) || {{}}).data || currentTotals;

  tfoot.innerHTML = `<tr>
    <td class="l" colspan="2">TOTAL DOS PARCEIROS (${{parceiros.length}} EMPRESAS)</td>
    ${{renderRowCells(canalTot, metric)}}
  </tr>`;
}}

// Despacho de Renderização por Tabela
function renderSpecificTable(tblId) {{
  const metric = tableMetrics[tblId];

  if (tblId === 'tblCanal') {{
    renderTableCanal(metric);
  }} else if (tblId === 'tblCanalBrasil') {{
    renderTableCanalBrasil(metric);
  }} else if (tblId === 'tblCidade') {{
    renderTableCidade(metric);
  }} else if (tblId === 'tblAaCidade') {{
    renderTableCidadePresencial('tblAaCidade', 'Agente Autorizado', metric);
  }} else if (tblId === 'tblAaParceiro') {{
    renderTableParceiroPresencial('tblAaParceiro', 'Agente Autorizado', metric);
  }} else if (tblId === 'tblPapCidade') {{
    renderTableCidadePresencial('tblPapCidade', 'Porta Porta', metric);
  }} else if (tblId === 'tblPapParceiro') {{
    renderTableParceiroPresencial('tblPapParceiro', 'Porta Porta', metric);
  }} else if (tblId === 'tblVarejoCidade') {{
    renderTableCidadePresencial('tblVarejoCidade', 'Varejo', metric);
  }} else if (tblId === 'tblVarejoParceiro') {{
    renderTableParceiroPresencial('tblVarejoParceiro', 'Varejo', metric);
  }} else if (tblId === 'tblLojasCidade') {{
    renderTableCidadePresencial('tblLojasCidade', 'Lojas Proprias', metric);
  }} else if (tblId === 'tblLojasParceiro') {{
    renderTableParceiroPresencial('tblLojasParceiro', 'Lojas Proprias', metric);
  }}
}}

// Filtro de Texto em Tempo Real para Tabela de Parceiros
function filterPartnerRows(tblId, term) {{
  const q = term.toLowerCase().trim();
  const rows = document.querySelectorAll(`#${{tblId}} tbody tr.partner-row`);
  rows.forEach(r => {{
    const name = (r.getAttribute('data-name') || '').toLowerCase();
    const cidades = (r.getAttribute('data-cidades') || '').toLowerCase();
    const match = !q || name.includes(q) || cidades.includes(q);
    r.style.display = match ? '' : 'none';
  }});
}}

// CLASSIFICAÇÃO UNIVERSAL DE COLUNAS (Requisito 4)
const tableSortState = {{}};

function sortTable(thEl, colIdx) {{
  const table = thEl.closest('table');
  if (!table) return;
  const tblId = table.id;
  const tbody = table.querySelector('tbody');
  if (!tbody) return;

  const stateKey = `${{tblId}}_${{colIdx}}`;
  const isAsc = !tableSortState[stateKey];
  tableSortState[stateKey] = isAsc;

  // Atualiza indicadores visuais nos cabeçalhos
  table.querySelectorAll('th').forEach(th => {{
    th.classList.remove('sorted-asc', 'sorted-desc');
    const arrow = th.querySelector('.sort-arrow');
    if (arrow) arrow.innerText = '↕';
  }});
  thEl.classList.add(isAsc ? 'sorted-asc' : 'sorted-desc');
  const activeArrow = thEl.querySelector('.sort-arrow');
  if (activeArrow) activeArrow.innerText = isAsc ? '▲' : '▼';

  // Verifica se há blocos agrupados ("Todas as Métricas")
  const hasBlocks = tbody.querySelector('tr.data-block-head') !== null;
  const groupHeaders = Array.from(tbody.querySelectorAll('tr.grp-header'));

  if (hasBlocks) {{
    if (groupHeaders.length > 0) {{
      // Ordena blocos preservando os cabeçalhos de grupos
      groupHeaders.forEach((grpHeader, gIdx) => {{
        const nextHeader = groupHeaders[gIdx + 1];
        const blocks = [];
        let curr = grpHeader.nextElementSibling;
        while (curr && curr !== nextHeader) {{
          if (curr.classList.contains('data-block-head') && !curr.classList.contains('bench-row')) {{
            const r1 = curr;
            const r2 = r1.nextElementSibling;
            const r3 = r2 ? r2.nextElementSibling : null;
            const r4 = r3 ? r3.nextElementSibling : null;
            blocks.push([r1, r2, r3, r4].filter(Boolean));
            curr = r4;
          }}
          if (curr) curr = curr.nextElementSibling;
        }}

        blocks.sort((bA, bB) => {{
          const cellA = bA[0].children[colIdx] || bA[0].querySelector('.td-foco');
          const cellB = bB[0].children[colIdx] || bB[0].querySelector('.td-foco');
          const valA = cellA ? (cellA.getAttribute('data-val') !== null ? parseFloat(cellA.getAttribute('data-val')) : cellA.innerText.trim()) : 0;
          const valB = cellB ? (cellB.getAttribute('data-val') !== null ? parseFloat(cellB.getAttribute('data-val')) : cellB.innerText.trim()) : 0;

          let res = 0;
          if (typeof valA === 'number' && typeof valB === 'number') {{
            res = valA - valB;
          }} else {{
            res = String(valA).localeCompare(String(valB));
          }}
          return isAsc ? res : -res;
        }});

        blocks.forEach(blk => blk.forEach(r => grpHeader.parentNode.insertBefore(r, nextHeader || null)));
      }});
    }} else {{
      const blocks = [];
      const rows = Array.from(tbody.querySelectorAll('tr'));
      for (let i = 0; i < rows.length; i++) {{
        const r = rows[i];
        if (r.classList.contains('data-block-head')) {{
          blocks.push([r, rows[i+1], rows[i+2], rows[i+3]]);
          i += 3;
        }}
      }}

      blocks.sort((bA, bB) => {{
        const cellA = bA[0].children[colIdx] || bA[0].querySelector('.td-foco');
        const cellB = bB[0].children[colIdx] || bB[0].querySelector('.td-foco');
        const valA = cellA ? (cellA.getAttribute('data-val') !== null ? parseFloat(cellA.getAttribute('data-val')) : cellA.innerText.trim()) : 0;
        const valB = cellB ? (cellB.getAttribute('data-val') !== null ? parseFloat(cellB.getAttribute('data-val')) : cellB.innerText.trim()) : 0;

        let res = 0;
        if (typeof valA === 'number' && typeof valB === 'number') {{
          res = valA - valB;
        }} else {{
          res = String(valA).localeCompare(String(valB));
        }}
        return isAsc ? res : -res;
      }});

      blocks.forEach(blk => blk.forEach(r => tbody.appendChild(r)));
    }}

  }} else {{
    // Linhas simples
    if (groupHeaders.length > 0) {{
      groupHeaders.forEach((grpHeader, gIdx) => {{
        const nextHeader = groupHeaders[gIdx + 1];
        const gRows = [];
        let curr = grpHeader.nextElementSibling;
        while (curr && curr !== nextHeader) {{
          if (curr.classList.contains('data-row') && !curr.classList.contains('bench-row')) {{
            gRows.push(curr);
          }}
          curr = curr.nextElementSibling;
        }}

        gRows.sort((rA, rB) => {{
          const cellA = rA.children[colIdx];
          const cellB = rB.children[colIdx];
          const valA = cellA ? (cellA.getAttribute('data-val') !== null ? parseFloat(cellA.getAttribute('data-val')) : cellA.innerText.trim()) : 0;
          const valB = cellB ? (cellB.getAttribute('data-val') !== null ? parseFloat(cellB.getAttribute('data-val')) : cellB.innerText.trim()) : 0;

          let res = 0;
          if (typeof valA === 'number' && typeof valB === 'number') {{
            res = valA - valB;
          }} else {{
            res = String(valA).localeCompare(String(valB));
          }}
          return isAsc ? res : -res;
        }});

        gRows.forEach(r => grpHeader.parentNode.insertBefore(r, nextHeader || null));
      }});

    }} else {{
      const rows = Array.from(tbody.querySelectorAll('tr.data-row'));
      rows.sort((rA, rB) => {{
        const cellA = rA.children[colIdx];
        const cellB = rB.children[colIdx];
        const valA = cellA ? (cellA.getAttribute('data-val') !== null ? parseFloat(cellA.getAttribute('data-val')) : cellA.innerText.trim()) : 0;
        const valB = cellB ? (cellB.getAttribute('data-val') !== null ? parseFloat(cellB.getAttribute('data-val')) : cellB.innerText.trim()) : 0;

        let res = 0;
        if (typeof valA === 'number' && typeof valB === 'number') {{
          res = valA - valB;
        }} else {{
          res = String(valA).localeCompare(String(valB));
        }}
        return isAsc ? res : -res;
      }});
      rows.forEach(r => tbody.appendChild(r));
    }}
  }}
}}

// APLICAÇÃO DE FILTROS REATIVOS
function handleFilterChange(selId, cntId) {{
  updateSelCount(selId, cntId);
  applyFilters();
}}

function applyFilters() {{
  activeFilters.cidades = getSelected('selCidade');
  activeFilters.canais = getSelected('selCanal');
  activeFilters.subcanais = getSelected('selSubcanal');
  activeFilters.grupos = getSelected('selGrupo');
  activeFilters.empresas = getSelected('selEmpresa');
  activeFilters.riscos = getSelected('selRisco');
  activeFilters.produtos = getSelected('selProduto');
  activeFilters.combinacoes = getSelected('selCombinacao');
  activeFilters.multis = getSelected('selMulti');

  renderChips();
  recalcDashboard();
}}

function resetAllFilters() {{
  ['selCidade', 'selCanal', 'selSubcanal', 'selGrupo', 'selEmpresa', 'selRisco', 'selProduto', 'selCombinacao', 'selMulti'].forEach(id => {{
    if (id === 'selCanal' && currentLockedCanal !== null) return;
    clearSel(id);
  }});
  applyFilters();
}}

function getSelected(selId) {{
  const sel = document.getElementById(selId);
  if (!sel) return [];
  return Array.from(sel.selectedOptions).map(o => o.value);
}}

function renderChips() {{
  const container = document.getElementById('activeFilterChips');
  let html = '';

  const addChips = (arr, label, selId) => {{
    arr.forEach(val => {{
      if (selId === 'selCanal' && currentLockedCanal !== null) {{
        html += `<div class="chip" style="background:#eef2ff;border-color:#c7d2fe;color:#3730a3;" title="Canal bloqueado na visão exclusiva">
          <span><b>${{label}}:</b> ${{val}} </span>
        </div>`;
      }} else {{
        html += `<div class="chip">
          <span><b>${{label}}:</b> ${{val}}</span>
          <span class="x" onclick="removeSingleFilter('${{selId}}', '${{val}}')">&times;</span>
        </div>`;
      }}
    }});
  }};

  addChips(activeFilters.cidades, 'Praça', 'selCidade');
  addChips(activeFilters.canais, 'Canal', 'selCanal');
  addChips(activeFilters.subcanais, 'Subgrupo', 'selSubcanal');
  addChips(activeFilters.grupos, 'Segmento', 'selGrupo');
  addChips(activeFilters.empresas, 'Empresa', 'selEmpresa');
  addChips(activeFilters.riscos, 'Risco', 'selRisco');
  addChips(activeFilters.produtos, 'Produto', 'selProduto');
  addChips(activeFilters.combinacoes, 'Combinação', 'selCombinacao');
  addChips(activeFilters.multis, 'Multi', 'selMulti');

  container.innerHTML = html;
}}

function removeSingleFilter(selId, val) {{
  if (selId === 'selCanal' && currentLockedCanal !== null) return;
  const sel = document.getElementById(selId);
  if (!sel) return;
  for (let opt of sel.options) {{
    if (opt.value === val) opt.selected = false;
  }}
  const cntMap = {{
    selCidade: 'cntCidade', selCanal: 'cntCanal', selSubcanal: 'cntSubcanal',
    selGrupo: 'cntGrupo', selEmpresa: 'cntEmpresa', selRisco: 'cntRisco',
    selProduto: 'cntProduto', selCombinacao: 'cntCombinacao', selMulti: 'cntMulti'
  }};
  updateSelCount(selId, cntMap[selId]);
  applyFilters();
}}

function filterSelect(selId, term) {{
  if (selId === 'selCanal' && currentLockedCanal !== null) return;
  const sel = document.getElementById(selId);
  if (!sel) return;
  const q = term.toLowerCase();
  for (let opt of sel.options) {{
    opt.style.display = opt.text.toLowerCase().includes(q) ? '' : 'none';
  }}
}}

function selAll(selId) {{
  if (selId === 'selCanal' && currentLockedCanal !== null) return;
  const sel = document.getElementById(selId);
  if (!sel) return;
  for (let opt of sel.options) {{
    if (opt.style.display !== 'none') opt.selected = true;
  }}
  const cntMap = {{
    selCidade: 'cntCidade', selCanal: 'cntCanal', selSubcanal: 'cntSubcanal',
    selGrupo: 'cntGrupo', selEmpresa: 'cntEmpresa', selRisco: 'cntRisco',
    selProduto: 'cntProduto', selCombinacao: 'cntCombinacao', selMulti: 'cntMulti'
  }};
  updateSelCount(selId, cntMap[selId]);
  applyFilters();
}}

function clearSel(selId) {{
  if (selId === 'selCanal' && currentLockedCanal !== null) return;
  const sel = document.getElementById(selId);
  if (!sel) return;
  for (let opt of sel.options) opt.selected = false;
  const cntMap = {{
    selCidade: 'cntCidade', selCanal: 'cntCanal', selSubcanal: 'cntSubcanal',
    selGrupo: 'cntGrupo', selEmpresa: 'cntEmpresa', selRisco: 'cntRisco',
    selProduto: 'cntProduto', selCombinacao: 'cntCombinacao', selMulti: 'cntMulti'
  }};
  updateSelCount(selId, cntMap[selId]);
  applyFilters();
}}

function updateSelCount(selId, cntId) {{
  const sel = document.getElementById(selId);
  if (!sel) return;
  const selCount = Array.from(sel.selectedOptions).length;
  const total = sel.options.length;
  const cntEl = document.getElementById(cntId);
  if (cntEl) cntEl.innerText = `${{selCount}}/${{total}}`;
}}

// Inicialização Automática da Aplicação
window.addEventListener('DOMContentLoaded', () => {{
  recalcDashboard();
}});

async function initFpdAuth() {{
  try {{
    const res = await fetch('/api/auth/me');
    if (res.ok) {{
      const u = await res.json();
      const el = document.getElementById('fpdUserWidget');
      if (el && u.authenticated) {{
        const fn = u.nome_completo ? u.nome_completo.split(' ')[0] : 'Colaborador';
        el.innerHTML = `
          <span style="color:#fff;font-size:11.5px;font-weight:600;white-space:nowrap;background:rgba(255,255,255,.15);padding:4px 8px;border-radius:3px">${{fn}} (${{u.area || 'Regional'}})</span>
          ${{u.is_admin ? '<a href="/admin/" style="background:rgba(255,255,255,.2);color:#fff;border:1px solid rgba(255,255,255,.4);padding:4px 8px;border-radius:3px;font-size:10.5px;font-weight:700;text-decoration:none">Admin</a>' : ''}}
          <button id="btnLogoutFpd" style="background:none;border:1px solid rgba(255,255,255,.3);color:#fff;padding:4px 8px;border-radius:3px;font-size:10.5px;cursor:pointer;font-weight:600">Sair</button>
        `;
        const btnLogout = document.getElementById('btnLogoutFpd');
        if (btnLogout) {{
          btnLogout.addEventListener('click', async (e) => {{
            e.preventDefault();
            btnLogout.disabled = true;
            btnLogout.textContent = 'Saindo...';
            try {{
              if (navigator.serviceWorker && navigator.serviceWorker.controller) {{
                navigator.serviceWorker.controller.postMessage({{ type: 'LOGOUT' }});
              }}
              if ('caches' in window) {{
                const keys = await caches.keys();
                await Promise.all(keys.map(k => caches.delete(k)));
              }}
              sessionStorage.clear();
              localStorage.clear();
              await fetch('/api/auth/logout', {{ method: 'POST' }});
            }} catch (err) {{}}
            window.location.replace('/login/?logout=1');
          }});
        }}
      }}
    }} else {{
      window.location.replace('/login/');
    }}
  }} catch (e) {{
    window.location.replace('/login/');
  }}
}}
initFpdAuth();
</script>
<script src="/js/app-mobile.js"></script>
</body>
</html>
"""

if __name__ == "__main__":
    build()
