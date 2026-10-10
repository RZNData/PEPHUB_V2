import openpyxl
import pyxlsb
import pandas as pd
import json
import os

def resolve_data_file(filename):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        filename,
        os.path.join(script_dir, filename),
        os.path.join(script_dir, '..', 'dados', filename),
        os.path.join(os.getcwd(), 'relatorios', 'churn_bl_total', 'dados', filename),
        os.path.join(os.getcwd(), 'relatorios', 'churn_bl_pme', 'dados', filename),
        os.path.join(os.getcwd(), filename)
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    # Fallback to prefix matching in dados
    for d in [os.path.join(script_dir, '..', 'dados'), os.path.join(os.getcwd(), 'relatorios', 'churn_bl_total', 'dados')]:
        if os.path.exists(d):
            prefix = filename.split('.')[0][:8].lower()
            for f in os.listdir(d):
                if prefix in f.lower():
                    return os.path.join(d, f)
    return filename


def parse_num(v):
    if v is None or pd.isna(v): return None
    s = str(v).strip().replace(' ', '')
    if s in ['', '-', '#DIV/0!', 'nan', 'None']: return None
    if '.' in s and ',' not in s:
        parts = s.split('.')
        if len(parts) == 2 and len(parts[1]) == 3:
            s = s.replace('.', '')
    elif ',' in s:
        s = s.replace('.', '').replace(',', '.')
    try:
        return float(s)
    except:
        return None

def normalize_city_id(name):
    s = str(name).upper().replace('Ã','A').replace('Á','A').replace('Â','A').replace('É','E').replace('Í','I').replace('Ó','O').replace('Ú','U').replace('Ç','C').strip()
    s = s.replace(' ', '_').replace('-', '_')
    if 'SAO_LUIS' in s or 'SAO_LUIZ' in s: return 'SAO_LUIS'
    if 'BELEM' in s: return 'BELEM'
    if 'GM_NORTE' in s or 'GRANDES' in s: return 'GM'
    if 'MD_NORTE' in s or 'DESENVOLVIMENTO' in s: return 'MD'
    if s == 'NORTE': return 'NORTE'
    return s

cities_meta = [
    {'id': 'NORTE', 'nome': 'Regional Norte', 'tipo': 'TOTAL', 'grupo': 'REGIONAL', 'uf': 'RNO'},
    {'id': 'GM', 'nome': 'Grandes Mercados', 'tipo': 'SUBTOTAL', 'grupo': 'GM', 'uf': 'GM'},
    {'id': 'ANANINDEUA', 'nome': 'Ananindeua', 'tipo': 'CIDADE', 'grupo': 'GM', 'uf': 'PA'},
    {'id': 'BELEM', 'nome': 'Belém', 'tipo': 'CIDADE', 'grupo': 'GM', 'uf': 'PA'},
    {'id': 'MACAPA', 'nome': 'Macapá', 'tipo': 'CIDADE', 'grupo': 'GM', 'uf': 'AP'},
    {'id': 'MANAUS', 'nome': 'Manaus', 'tipo': 'CIDADE', 'grupo': 'GM', 'uf': 'AM'},
    {'id': 'SANTANA', 'nome': 'Santana', 'tipo': 'CIDADE', 'grupo': 'GM', 'uf': 'AP'},
    {'id': 'SAO_LUIS', 'nome': 'São Luís', 'tipo': 'CIDADE', 'grupo': 'GM', 'uf': 'MA'},
    {'id': 'MD', 'nome': 'Mercados em Desenvolvimento', 'tipo': 'SUBTOTAL', 'grupo': 'MD', 'uf': 'MD'},
    {'id': 'CASTANHAL', 'nome': 'Castanhal', 'tipo': 'CIDADE', 'grupo': 'MD', 'uf': 'PA'},
    {'id': 'CAXIAS', 'nome': 'Caxias', 'tipo': 'CIDADE', 'grupo': 'MD', 'uf': 'MA'},
    {'id': 'IMPERATRIZ', 'nome': 'Imperatriz', 'tipo': 'CIDADE', 'grupo': 'MD', 'uf': 'MA'},
    {'id': 'MARABA', 'nome': 'Marabá', 'tipo': 'CIDADE', 'grupo': 'MD', 'uf': 'PA'},
    {'id': 'PARAGOMINAS', 'nome': 'Paragominas', 'tipo': 'CIDADE', 'grupo': 'MD', 'uf': 'PA'},
    {'id': 'PARAUAPEBAS', 'nome': 'Parauapebas', 'tipo': 'CIDADE', 'grupo': 'MD', 'uf': 'PA'},
    {'id': 'TIMON', 'nome': 'Timon', 'tipo': 'CIDADE', 'grupo': 'MD', 'uf': 'MA'}
]

MONTH_NAMES = [
    ('2024-01', 'Jan/24'), ('2024-02', 'Fev/24'), ('2024-03', 'Mar/24'),
    ('2024-04', 'Abr/24'), ('2024-05', 'Mai/24'), ('2024-06', 'Jun/24'),
    ('2024-07', 'Jul/24'), ('2024-08', 'Ago/24'), ('2024-09', 'Set/24'),
    ('2024-10', 'Out/24'), ('2024-11', 'Nov/24'), ('2024-12', 'Dez/24'),
    ('2025-01', 'Jan/25'), ('2025-02', 'Fev/25'), ('2025-03', 'Mar/25'),
    ('2025-04', 'Abr/25'), ('2025-05', 'Mai/25'), ('2025-06', 'Jun/25'),
    ('2025-07', 'Jul/25'), ('2025-08', 'Ago/25'), ('2025-09', 'Set/25'),
    ('2025-10', 'Out/25'), ('2025-11', 'Nov/25'), ('2025-12', 'Dez/25'),
    ('2026-01', 'Jan/26'), ('2026-02', 'Fev/26'), ('2026-03', 'Mar/26'),
    ('2026-04', 'Abr/26'), ('2026-05', 'Mai/26'), ('2026-06', 'Jun/26'),
    ('2026-07', 'Jul/26'), ('2026-08', 'Ago/26'), ('2026-09', 'Set/26'),
    ('2026-10', 'Out/26')
]

MONTHS_21_KEYS = [
    ('2025-01', 'Jan/25', ['jan/25', 'j/25']),
    ('2025-02', 'Fev/25', ['fev/25', 'f/25']),
    ('2025-03', 'Mar/25', ['mar/25', 'm/25']),
    ('2025-04', 'Abr/25', ['abr/25', 'a/25']),
    ('2025-05', 'Mai/25', ['mai/25', 'm/25']),
    ('2025-06', 'Jun/25', ['jun/25', 'j/25']),
    ('2025-07', 'Jul/25', ['jul/25', 'j/25']),
    ('2025-08', 'Ago/25', ['ago/25', 'a/25']),
    ('2025-09', 'Set/25', ['set/25', 's/25']),
    ('2025-10', 'Out/25', ['out/25', 'o/25']),
    ('2025-11', 'Nov/25', ['nov/25', 'n/25']),
    ('2025-12', 'Dez/25', ['dez/25', 'd/25']),
    ('2026-01', 'Jan/26', ['jan/26', 'j/26']),
    ('2026-02', 'Fev/26', ['fev/26', 'f/26']),
    ('2026-03', 'Mar/26', ['mar/26', 'm/26']),
    ('2026-04', 'Abr/26', ['abr/26', 'a/26']),
    ('2026-05', 'Mai/26', ['mai/26', 'm/26']),
    ('2026-06', 'Jun/26', ['jun/26', 'j/26']),
    ('2026-07', 'Jul/26', ['jul/26', 'j/26']),
    ('2026-08', 'Ago/26', ['ago/26', 'a/26']),
    ('2026-09', 'Set/26', ['set/26', 's/26'])
]

CC_MONTHS_META = [
    ('2025-01', 'Jan/25', 0), ('2025-02', 'Fev/25', 1), ('2025-03', 'Mar/25', 2),
    ('2025-04', 'Abr/25', 3), ('2025-05', 'Mai/25', 4), ('2025-06', 'Jun/25', 5),
    ('2025-07', 'Jul/25', 6), ('2025-08', 'Ago/25', 7), ('2025-09', 'Set/25', 8),
    ('2025-10', 'Out/25', 9), ('2025-11', 'Nov/25', 10), ('2025-12', 'Dez/25', 11),
    ('2026-01', 'Jan/26', 12), ('2026-02', 'Fev/26', 13), ('2026-03', 'Mar/26', 14),
    ('2026-04', 'Abr/26', 15), ('2026-05', 'Mai/26', 16), ('2026-06', 'Jun/26', 17),
    ('2026-07', 'Jul/26', 18), ('2026-08', 'Ago/26', 19), ('2026-09', 'Set/26', 20)
]

SPEECH_MONTHS = [
    ('Jan/26', '2026-01'), ('Fev/26', '2026-02'), ('Mar/26', '2026-03'),
    ('Abr/26', '2026-04'), ('Mai/26', '2026-05'), ('Jun/26', '2026-06'),
    ('Jul/26', '2026-07'), ('Ago/26', '2026-08'), ('Set/26', '2026-09')
]

SPEECH_CATS_META = [
    {'id': 'acha_caro', 'speech': 'Acha Caro / Aumento no Valor', 'idx': 0, 'color': '#c98a15'},
    {'id': 'reajuste', 'speech': 'Reajuste / Aumento de Valor', 'idx': 1, 'color': '#e67e22'},
    {'id': 'pouca_util', 'speech': 'Sem / Pouca Utilização', 'idx': 2, 'color': '#7f8c8d'},
    {'id': 'nao_pedi', 'speech': 'Não Pedi / Solicitei', 'idx': 3, 'color': '#95a5a6'},
    {'id': 'tecnico', 'speech': 'Técnico - Internet', 'idx': 4, 'color': '#2980b9'},
    {'id': 'concorrencia', 'speech': 'Concorrência', 'idx': 5, 'color': '#f39c12'},
    {'id': 'financeiro', 'speech': 'Dificuldade Financeira / Reclama do Valor', 'idx': 6, 'color': '#16a085'},
    {'id': 'consulta_val', 'speech': 'Não Concorda e/ou Consulta Valores', 'idx': 7, 'color': '#8e44ad'},
    {'id': 'mudanca_end', 'speech': 'Mudança de Endereço', 'idx': 8, 'color': '#c0392b'}
]

def build_invol_pillar_metrics(s26_vals, a26_vals, s25_vals, base_real):
    fpd, fraude, base, opcao, total = s26_vals
    a_fpd, a_fraude, a_base, a_opcao, a_total = a26_vals
    y_fpd, y_fraude, y_base, y_opcao, y_total = s25_vals
    
    total = total if total > 0 else (fpd + fraude + base + opcao)
    a_total = a_total if a_total > 0 else (a_fpd + a_fraude + a_base + a_opcao)
    y_total = y_total if y_total > 0 else (y_fpd + y_fraude + y_base + y_opcao)

    def calc_pct(part, tot):
        return round((part / tot * 100), 1) if tot > 0 else 0.0

    def calc_var(cur, prev):
        return round(((cur - prev) / prev * 100), 1) if prev > 0 else 0.0

    def calc_taxa(vol, b):
        return round((vol / b * 100), 2) if b > 0 else 0.0

    return {
        'fpd': round(fpd, 1),
        'fraude': round(fraude, 1),
        'invol_base': round(base, 1),
        'opcao': round(opcao, 1),
        'total': round(total, 1),
        'base_real': int(base_real) if base_real else 0,

        # Participação % no total de involuntárias
        'pct_base': calc_pct(base, total),
        'pct_fpd': calc_pct(fpd, total),
        'pct_opcao': calc_pct(opcao, total),
        'pct_fraude': calc_pct(fraude, total),

        # MoM (%)
        'mom_base_pct': calc_var(base, a_base),
        'mom_fpd_pct': calc_var(fpd, a_fpd),
        'mom_opcao_pct': calc_var(opcao, a_opcao),
        'mom_fraude_pct': calc_var(fraude, a_fraude),
        'mom_total_pct': calc_var(total, a_total),

        # YoY (%)
        'yoy_base_pct': calc_var(base, y_base),
        'yoy_fpd_pct': calc_var(fpd, y_fpd),
        'yoy_opcao_pct': calc_var(opcao, y_opcao),
        'yoy_fraude_pct': calc_var(fraude, y_fraude),
        'yoy_total_pct': calc_var(total, y_total),

        # Taxa de Churn (% da Base Real)
        'taxa_base': calc_taxa(base, base_real),
        'taxa_fpd': calc_taxa(fpd, base_real),
        'taxa_opcao': calc_taxa(opcao, base_real),
        'taxa_fraude': calc_taxa(fraude, base_real),
        'taxa_total': calc_taxa(total, base_real),
    }

def extract_involuntary_projection(is_pme=False, bases_map=None):
    """Extrai o Modelo de Projeção Residencial (Banda Larga) com histórico de 21 meses, MoM, YoY e Taxas sobre a Base"""
    if bases_map is None: bases_map = {}
    proj_path = resolve_data_file('MODELO_PROJEÇÃO_CIDADE_RESIDENCIAL - SET S4_V2.xlsb')
    sheet_name = 'ÁREA CABEADA PME' if is_pme else 'ÁREA CABEADA TOTAL'
    print(f"Lendo Modelo Projeção Involuntária de {sheet_name}...")
    df_proj = pd.read_excel(proj_path, engine='pyxlsb', sheet_name=sheet_name, header=None)

    # 1. Encontrar faixa de colunas de Banda Larga
    bl_start = 231 if is_pme else 236
    bl_end = 466
    for c in range(df_proj.shape[1]):
        val = str(df_proj.iloc[1, c]).upper()
        if 'BANDA LARGA' in val: bl_start = c
        if 'TV' in val and c > bl_start:
            bl_end = c
            break

    # 2. Mapear dinamicamente os 21 meses
    col_map = {}
    for c in range(bl_start, bl_end):
        m = str(df_proj.iloc[2, c]).strip().lower()
        if m and m != 'nan':
            for iso, lbl, patterns in MONTHS_21_KEYS:
                if any(p in m for p in patterns):
                    col_map.setdefault(iso, []).append((c, m))

    final_month_cols = []
    for iso, lbl, patterns in MONTHS_21_KEYS:
        candidates = col_map.get(iso, [])
        if not candidates: continue
        best = None
        for c, m in candidates:
            if 'fech' in m: best = c; break
            if 's4' in m: best = c
        if best is None: best = candidates[-1][0]
        final_month_cols.append((iso, lbl, best))

    col_by_iso = {iso: c for iso, lbl, c in final_month_cols}
    c_s26 = col_by_iso.get('2026-09', final_month_cols[-1][2])
    c_a26 = col_by_iso.get('2026-08', c_s26)
    c_s25 = col_by_iso.get('2025-09', c_s26)
    r_rno = 11

    # 3. Mapear praças/cidades
    city_rows = {}
    for r in range(21, df_proj.shape[0]):
        reg_val = df_proj.iloc[r, 3]
        if str(reg_val).strip().upper() == 'RNO':
            c_name = df_proj.iloc[r, 1]
            cid = normalize_city_id(c_name)
            city_rows[cid] = r

    gm_cities = ['ANANINDEUA', 'BELEM', 'MACAPA', 'MANAUS', 'SANTANA', 'SAO_LUIS']
    md_cities = ['CASTANHAL', 'CAXIAS', 'IMPERATRIZ', 'MARABA', 'PARAGOMINAS', 'PARAUAPEBAS', 'TIMON']

    def get_row_tuple(r, col_idx):
        fpd = parse_num(df_proj.iloc[r, col_idx]) or 0
        fraude = parse_num(df_proj.iloc[r, col_idx+1]) or 0
        invol_base = parse_num(df_proj.iloc[r, col_idx+2]) or 0
        opcao = parse_num(df_proj.iloc[r, col_idx+3]) or 0
        total = parse_num(df_proj.iloc[r, col_idx+4]) or (fpd + fraude + invol_base + opcao)
        return (fpd, fraude, invol_base, opcao, total)

    cities_proj = {}
    for cid, r in city_rows.items():
        s26 = get_row_tuple(r, c_s26)
        a26 = get_row_tuple(r, c_a26)
        s25 = get_row_tuple(r, c_s25)
        b_real = bases_map.get(cid, 0)
        cities_proj[cid] = build_invol_pillar_metrics(s26, a26, s25, b_real)

    def sum_tuples(tuples):
        return (
            sum(t[0] for t in tuples),
            sum(t[1] for t in tuples),
            sum(t[2] for t in tuples),
            sum(t[3] for t in tuples),
            sum(t[4] for t in tuples)
        )

    # GM
    gm_s26 = sum_tuples([get_row_tuple(city_rows[c], c_s26) for c in gm_cities if c in city_rows])
    gm_a26 = sum_tuples([get_row_tuple(city_rows[c], c_a26) for c in gm_cities if c in city_rows])
    gm_s25 = sum_tuples([get_row_tuple(city_rows[c], c_s25) for c in gm_cities if c in city_rows])
    gm_proj = build_invol_pillar_metrics(gm_s26, gm_a26, gm_s25, bases_map.get('GM', 0))

    # MD
    md_s26 = sum_tuples([get_row_tuple(city_rows[c], c_s26) for c in md_cities if c in city_rows])
    md_a26 = sum_tuples([get_row_tuple(city_rows[c], c_a26) for c in md_cities if c in city_rows])
    md_s25 = sum_tuples([get_row_tuple(city_rows[c], c_s25) for c in md_cities if c in city_rows])
    md_proj = build_invol_pillar_metrics(md_s26, md_a26, md_s25, bases_map.get('MD', 0))

    # Regional Norte
    reg_s26 = get_row_tuple(r_rno, c_s26)
    reg_a26 = get_row_tuple(r_rno, c_a26)
    reg_s25 = get_row_tuple(r_rno, c_s25)
    reg_proj = build_invol_pillar_metrics(reg_s26, reg_a26, reg_s25, bases_map.get('NORTE', 0))

    # 4. Histórico 21 meses das Aberturas do Involuntário (Regional, GM, MD, e Cidades)
    invol_history = []
    for iso, lbl, c in final_month_cols:
        h_fpd = parse_num(df_proj.iloc[r_rno, c]) or 0
        h_fraude = parse_num(df_proj.iloc[r_rno, c+1]) or 0
        h_base = parse_num(df_proj.iloc[r_rno, c+2]) or 0
        h_opcao = parse_num(df_proj.iloc[r_rno, c+3]) or 0
        h_total = parse_num(df_proj.iloc[r_rno, c+4]) or (h_fpd + h_fraude + h_base + h_opcao)

        gm_tot = {'fpd': 0, 'fraude': 0, 'invol_base': 0, 'opcao': 0, 'total': 0}
        md_tot = {'fpd': 0, 'fraude': 0, 'invol_base': 0, 'opcao': 0, 'total': 0}
        c_tot = {}

        for g_c in gm_cities:
            if g_c in city_rows:
                r_c = city_rows[g_c]
                t_c = get_row_tuple(r_c, c)
                gm_tot['fpd'] += t_c[0]
                gm_tot['fraude'] += t_c[1]
                gm_tot['invol_base'] += t_c[2]
                gm_tot['opcao'] += t_c[3]
                gm_tot['total'] += t_c[4]
                c_tot[g_c] = {'fpd': round(t_c[0], 1), 'fraude': round(t_c[1], 1), 'invol_base': round(t_c[2], 1), 'opcao': round(t_c[3], 1), 'total': round(t_c[4], 1)}

        for m_c in md_cities:
            if m_c in city_rows:
                r_c = city_rows[m_c]
                t_c = get_row_tuple(r_c, c)
                md_tot['fpd'] += t_c[0]
                md_tot['fraude'] += t_c[1]
                md_tot['invol_base'] += t_c[2]
                md_tot['opcao'] += t_c[3]
                md_tot['total'] += t_c[4]
                c_tot[m_c] = {'fpd': round(t_c[0], 1), 'fraude': round(t_c[1], 1), 'invol_base': round(t_c[2], 1), 'opcao': round(t_c[3], 1), 'total': round(t_c[4], 1)}

        invol_history.append({
            'iso': iso,
            'label': lbl,
            'fpd': round(h_fpd, 1),
            'fraude': round(h_fraude, 1),
            'invol_base': round(h_base, 1),
            'opcao': round(h_opcao, 1),
            'total': round(h_total, 1),
            'gm': {k: round(v, 1) for k, v in gm_tot.items()},
            'md': {k: round(v, 1) for k, v in md_tot.items()},
            'cities': c_tot
        })

    return {
        'regional': reg_proj,
        'gm': gm_proj,
        'md': md_proj,
        'cities': cities_proj,
        'history': invol_history
    }

def extract_callcenter_summary(bases_map=None):
    """Extrai a inteligência e detalhamento de Call Center com histórico de 21 meses e Speech Analytics de 9 meses por praça"""
    if bases_map is None: bases_map = {}
    cc_path = resolve_data_file('SUMÁRIO - CALL CENTER - S4 - 092026.xlsb')
    print(f"Lendo inteligência de Call Center de {cc_path}...")
    df_base = pd.read_excel(cc_path, engine='pyxlsb', sheet_name='Base', header=None)
    df_m = pd.read_excel(cc_path, engine='pyxlsb', sheet_name='BLOCO MOTIVO URA', header=None)
    df_t = pd.read_excel(cc_path, engine='pyxlsb', sheet_name='BLOCO TAXA MOTIVO URA', header=None)

    row_map = {
        'NORTE': (287, 24),
        'GM': (285, 25),
        'MD': (286, 26),
        'MANAUS': (278, 48),
        'ANANINDEUA': (272, 49),
        'BELEM': (273, 50),
        'CASTANHAL': (274, 51),
        'MARABA': (279, 52),
        'PARAGOMINAS': (280, 53),
        'PARAUAPEBAS': (281, 54),
        'MACAPA': (277, 55),
        'SANTANA': (282, 56),
        'CAXIAS': (275, 61),
        'IMPERATRIZ': (276, 62),
        'SAO_LUIS': (283, 63),
        'TIMON': (284, 64)
    }

    c_atend = 26
    c_unicas = 47
    c_mix = 89
    c_tx_os = 110
    c_lead = 173
    c_os = 194
    c_perf = 215

    motives_config = [
        {
            'id': 'financeiro',
            'motivo': 'Financeiro',
            'c_call': 4,
            'c_os': 14,
            'c_mix_bloco': 15,
            'c_tx_bloco': 24,
            'c_mix_base': 363,
            'c_tx_base': 489,
            'color': '#2a5d8f',
            'dinamica': 'Alto Volume / Máxima Retenção (91,1% Revertido)',
            'perfil': 'Negociação & Faturas',
            'status': 'Controlado'
        },
        {
            'id': 'canc_auto',
            'motivo': 'Cancelamento Automático',
            'c_call': 6,
            'c_os': 16,
            'c_mix_bloco': 17,
            'c_tx_bloco': 26,
            'c_mix_base': 405,
            'c_tx_base': 531,
            'color': '#c0392b',
            'dinamica': 'Maior Ofensor Absoluto (32,4% das OS Emitidas)',
            'perfil': 'Fila Direta URA',
            'status': 'Alto'
        },
        {
            'id': 'concorrencia',
            'motivo': 'Concorrência',
            'c_call': 5,
            'c_os': 15,
            'c_mix_bloco': 16,
            'c_tx_bloco': 25,
            'c_mix_base': 384,
            'c_tx_base': 510,
            'color': '#c98a15',
            'dinamica': 'Forte Retenção Comercial (86,5% Revertido)',
            'perfil': 'Ofertas Competitivas',
            'status': 'Médio'
        },
        {
            'id': 'me',
            'motivo': 'Mudança de Endereço',
            'c_call': 8,
            'c_os': 18,
            'c_mix_bloco': 19,
            'c_tx_bloco': 28,
            'c_mix_base': 447,
            'c_tx_base': 573,
            'color': '#8a0f18',
            'dinamica': 'Máxima Letalidade (38,5% OS por Inviabilidade)',
            'perfil': 'Inviabilidade de Rede',
            'status': 'Crítico'
        },
        {
            'id': 'tecnico',
            'motivo': 'Técnico',
            'c_call': 7,
            'c_os': 17,
            'c_mix_bloco': 18,
            'c_tx_bloco': 27,
            'c_mix_base': 426,
            'c_tx_base': 552,
            'color': '#516173',
            'dinamica': 'Suporte Técnico Resolutivo (85,8% Revertido)',
            'perfil': 'Sinal & Equipamentos',
            'status': 'Médio'
        },
        {
            'id': 'atendimento',
            'motivo': 'Atendimento',
            'c_call': 9,
            'c_os': 19,
            'c_mix_bloco': 20,
            'c_tx_bloco': 29,
            'c_mix_base': 468,
            'c_tx_base': 594,
            'color': '#6b4b8a',
            'dinamica': 'Baixo Volume / Alta Resolução (89,4% Revertido)',
            'perfil': 'Atrito de Atendimento',
            'status': 'Moderado'
        }
    ]

    cities_cc = {}
    for cid, (r_base, r_bloco) in row_map.items():
        atend = parse_num(df_base.iloc[r_base, c_atend]) or 0
        unicas = parse_num(df_base.iloc[r_base, c_unicas]) or 0
        mix = parse_num(df_base.iloc[r_base, c_mix]) or 0
        tx_os = parse_num(df_base.iloc[r_base, c_tx_os]) or 0
        lead = parse_num(df_base.iloc[r_base, c_lead]) or 0
        os_g = parse_num(df_base.iloc[r_base, c_os]) or 0
        perf = parse_num(df_base.iloc[r_base, c_perf]) or 0

        ura_bloco_total = int(parse_num(df_m.iloc[r_bloco, 10]) or 0)
        base_real = bases_map.get(cid, 0)
        taxa_os_base = round((os_g / base_real) * 100, 2) if base_real > 0 else 0.0

        # Matriz dos 6 Motivos de Procura vs Taxa de OS com comparativos MoM, YoY e Taxa s/ Base
        m_matriz = []
        sum_calls = 0
        sum_os = 0
        for m in motives_config:
            calls = int(parse_num(df_m.iloc[r_bloco, m['c_call']]) or 0)
            os_val = int(parse_num(df_t.iloc[r_bloco, m['c_os']]) or 0)
            mix_pct = round((parse_num(df_m.iloc[r_bloco, m['c_mix_bloco']]) or 0) * 100, 1)
            tx_pct = round((parse_num(df_t.iloc[r_bloco, m['c_tx_bloco']]) or 0) * 100, 1)

            # MoM e YoY de Base
            mix_s26 = parse_num(df_base.iloc[r_base, m['c_mix_base'] + 20]) or 0
            mix_a26 = parse_num(df_base.iloc[r_base, m['c_mix_base'] + 19]) or 0
            mix_s25 = parse_num(df_base.iloc[r_base, m['c_mix_base'] + 8]) or 0

            tx_s26 = parse_num(df_base.iloc[r_base, m['c_tx_base'] + 20]) or 0
            tx_a26 = parse_num(df_base.iloc[r_base, m['c_tx_base'] + 19]) or 0
            tx_s25 = parse_num(df_base.iloc[r_base, m['c_tx_base'] + 8]) or 0

            sum_calls += calls
            sum_os += os_val

            mix_mom = round((mix_s26 - mix_a26) * 100, 1)
            mix_yoy = round((mix_s26 - mix_s25) * 100, 1)
            tx_mom = round((tx_s26 - tx_a26) * 100, 1)
            tx_yoy = round((tx_s26 - tx_s25) * 100, 1)
            ret_pct = round(100.0 - tx_pct, 1)
            div_pp = round(tx_pct - mix_pct, 1)
            taxa_motivo_base = round((os_val / base_real) * 100, 2) if base_real > 0 else 0.0

            m_matriz.append({
                'id': m['id'],
                'motivo': m['motivo'],
                'color': m['color'],
                'ligacoes': calls,
                'mix_pct': mix_pct,
                'mix_mom_pp': mix_mom,
                'mix_yoy_pp': mix_yoy,
                'os_geradas': os_val,
                'taxa_os_pct': tx_pct,
                'taxa_os_mom_pp': tx_mom,
                'taxa_os_yoy_pp': tx_yoy,
                'taxa_retencao_pct': ret_pct,
                'taxa_os_base': taxa_motivo_base,
                'divergencia_pp': div_pp,
                'dinamica': m['dinamica'],
                'perfil': m['perfil'],
                'status': m['status']
            })

        outros_calls = max(0, ura_bloco_total - sum_calls)

        # Histórico 21 meses do Call Center para este cid
        cc_history = []
        for iso, lbl, offset in CC_MONTHS_META:
            h_item = {'iso': iso, 'label': lbl, 'mix': {}, 'taxa_os': {}}
            for m in motives_config:
                v_m = parse_num(df_base.iloc[r_base, m['c_mix_base'] + offset])
                v_t = parse_num(df_base.iloc[r_base, m['c_tx_base'] + offset])
                h_item['mix'][m['id']] = round(v_m * 100, 1) if v_m is not None else 0.0
                h_item['taxa_os'][m['id']] = round(v_t * 100, 1) if v_t is not None else 0.0
            cc_history.append(h_item)

        # Speech Analytics: histórico de 9 meses e comparativos MoM/YTD
        speech_history = []
        for m, (lbl, iso) in enumerate(SPEECH_MONTHS):
            h_pt = {'label': lbl, 'iso': iso}
            for sc in SPEECH_CATS_META:
                val_pct = round((parse_num(df_base.iloc[r_base, 692 + m*9 + sc['idx']]) or 0) * 100, 1)
                h_pt[sc['id']] = val_pct
            speech_history.append(h_pt)

        speech_summary = []
        for sc in SPEECH_CATS_META:
            s26 = speech_history[-1][sc['id']]
            a26 = speech_history[-2][sc['id']]
            j26 = speech_history[0][sc['id']]
            mom_pp = round(s26 - a26, 1)
            ytd_pp = round(s26 - j26, 1)
            speech_summary.append({
                'id': sc['id'],
                'speech': sc['speech'],
                'color': sc['color'],
                'pct': s26,
                'mom_pp': mom_pp,
                'ytd_pp': ytd_pp,
                'tendencia': 'Alta' if mom_pp > 0.1 else ('Queda' if mom_pp < -0.1 else 'Estável')
            })

        cities_cc[cid] = {
            'atendidas': int(atend),
            'unicas': int(unicas),
            'ura': ura_bloco_total,
            'mix_ura': round(mix * 100, 1),
            'taxa_os': round(tx_os * 100, 1),
            'lead_unico': int(lead),
            'os_geradas': int(os_g),
            'performance': round(perf * 100, 1),
            'base_real': int(base_real),
            'taxa_os_base': taxa_os_base,
            'motivos_matriz': m_matriz,
            'motivos_total_calls': ura_bloco_total,
            'motivos_total_os': sum_os,
            'outros_calls': outros_calls,
            'history': cc_history,
            'speech_analytics': speech_summary,
            'speech_history': speech_history
        }

    # Motivos com maior taxa de OS na Regional Norte
    motivos_ranking = [
        {'motivo': 'Mudança de Endereço', 'taxa_os': round((parse_num(df_base.iloc[287, 593]) or 0.385) * 100, 1), 'status': 'Crítico', 'color': '#8a0f18'},
        {'motivo': 'Cancelamento Automático', 'taxa_os': round((parse_num(df_base.iloc[287, 551]) or 0.263) * 100, 1), 'status': 'Alto', 'color': '#c0392b'},
        {'motivo': 'Técnico', 'taxa_os': round((parse_num(df_base.iloc[287, 572]) or 0.142) * 100, 1), 'status': 'Médio', 'color': '#516173'},
        {'motivo': 'Concorrência', 'taxa_os': round((parse_num(df_base.iloc[287, 530]) or 0.135) * 100, 1), 'status': 'Médio', 'color': '#c98a15'},
        {'motivo': 'Atendimento', 'taxa_os': round((parse_num(df_base.iloc[287, 614]) or 0.106) * 100, 1), 'status': 'Moderado', 'color': '#6b4b8a'},
        {'motivo': 'Financeiro', 'taxa_os': round((parse_num(df_base.iloc[287, 509]) or 0.089) * 100, 1), 'status': 'Controlado', 'color': '#2a5d8f'}
    ]

    return {
        'regional': cities_cc['NORTE'],
        'gm': cities_cc['GM'],
        'md': cities_cc['MD'],
        'cities': cities_cc,
        'motivos_matriz': cities_cc['NORTE']['motivos_matriz'],
        'motivos_taxa_os': motivos_ranking,
        'speech_analytics': cities_cc['NORTE']['speech_analytics'],
        'speech_history': cities_cc['NORTE']['speech_history'],
        'speech_cats_meta': SPEECH_CATS_META,
        'speech_months': SPEECH_MONTHS,
        'history': cities_cc['NORTE']['history'],
        'motives_config': motives_config
    }

def extract_full_churn_data(filepath, segment_name, is_xlsb=False):
    print(f"Extracting {segment_name} from {filepath}...")
    if is_xlsb:
        df_ana = pd.read_excel(filepath, engine='pyxlsb', sheet_name=0, header=None)
        df_gr = pd.read_excel(filepath, engine='pyxlsb', sheet_name=2, header=None)
        base_rows = {'TOTAL': 5, 'VOLUNTARIA': 22, 'INVOLUNTARIA': 39}
        gr_offset = 45
        col_current = 69 # Out/26 (T1)
        col_mom = 68     # Set/26 (MoM)
        col_yoy = 57     # Out/25 (YoY)
        col_p1, col_p2, col_p3, col_p4 = 72, 73, 74, 75
        col_orc_current = None
        start_hist_col = 36 # Jan/24
        ytd_2026_range = range(60, 70) # Jan/26..Out/26 (10 meses)
        ytd_2025_range = range(48, 58) # Jan/25..Out/25 (10 meses)
        ytd_orc_range = []
    else:
        wb = openpyxl.load_workbook(filepath, data_only=True)
        ws_ana = wb.worksheets[0]
        ws_gr = wb.worksheets[2]
        df_ana = pd.DataFrame([[ws_ana.cell(r, c).value for c in range(1, 130)] for r in range(1, 65)])
        df_gr = pd.DataFrame([[ws_gr.cell(r, c).value for c in range(1, 65)] for r in range(1, 100)])
        wb.close()
        base_rows = {'TOTAL': 5, 'VOLUNTARIA': 22, 'INVOLUNTARIA': 39}
        gr_offset = 45
        col_current = 69 # Out/26 (T1)
        col_mom = 68     # Set/26 (MoM)
        col_yoy = 57     # Out/25 (YoY)
        col_p1, col_p2, col_p3, col_p4 = 72, 73, 74, 75
        col_orc_current = 111 # Out/26 Orçado
        start_hist_col = 36 # Jan/24
        start_orc_hist_col = 78 # Jan/24 Orçado
        ytd_2026_range = range(60, 70) # Jan/26..Out/26 (10 meses)
        ytd_2025_range = range(48, 58) # Jan/25..Out/25 (10 meses)
        ytd_orc_range = range(102, 112) # Jan/26..Out/26 Orçado

    modes_data = {}

    for mode_key in ['TOTAL', 'VOLUNTARIA', 'INVOLUNTARIA']:
        b_r = base_rows[mode_key]
        mode_label = "Desconexão Total" if mode_key == "TOTAL" else ("Desconexão Voluntária" if mode_key == "VOLUNTARIA" else "Desconexão Involuntária")
        
        cities_list = []
        for i, cm in enumerate(cities_meta):
            r = b_r + i
            r_gr = gr_offset + i
            
            v_curr = parse_num(df_ana.iloc[r, col_current]) or 0
            v_mom = parse_num(df_ana.iloc[r, col_mom]) or 0
            v_yoy = parse_num(df_ana.iloc[r, col_yoy]) or 0
            
            v_p1 = parse_num(df_ana.iloc[r, col_p1]) or v_curr
            v_p2 = parse_num(df_ana.iloc[r, col_p2]) or v_curr
            v_p3 = parse_num(df_ana.iloc[r, col_p3]) or v_curr
            v_p4 = parse_num(df_ana.iloc[r, col_p4]) or v_curr
            
            # YTD 2026 e YTD 2025
            ytd_2026_vals = [parse_num(df_ana.iloc[r, c]) for c in ytd_2026_range]
            ytd_2026 = sum([x for x in ytd_2026_vals if x is not None])
            
            ytd_2025_vals = [parse_num(df_ana.iloc[r, c]) for c in ytd_2025_range]
            ytd_2025 = sum([x for x in ytd_2025_vals if x is not None])

            ytd_26x25_delta = round(ytd_2026 - ytd_2025, 1)
            ytd_26x25_pct = round(((ytd_2026 - ytd_2025) / ytd_2025) * 100, 2) if ytd_2025 > 0 else 0

            if is_xlsb:
                v_orc = None
                d_rxo = None
                pct_rxo = None
                ytd_orc = None
                ytd_rxo_delta = None
                ytd_rxo_pct = None
                base_real = parse_num(df_gr.iloc[r_gr, 4]) if df_gr.shape[0] > r_gr and df_gr.shape[1] > 4 else None
                base_orc = None
                taxa_real = round((v_curr / base_real) * 100, 2) if (base_real and base_real > 0 and v_curr is not None) else None
                taxa_orc = None
                taxa_delta_pp = None
            else:
                v_orc = parse_num(df_ana.iloc[r, col_orc_current]) if (col_orc_current and df_ana.shape[1] > col_orc_current) else None
                d_rxo = round(v_curr - v_orc, 1) if (v_curr is not None and v_orc is not None) else None
                pct_rxo = round(((v_curr - v_orc) / v_orc) * 100, 2) if (v_orc and v_orc > 0 and v_curr is not None) else None

                ytd_orc_vals = [parse_num(df_ana.iloc[r, c]) for c in ytd_orc_range] if len(ytd_orc_range) > 0 and df_ana.shape[1] > max(ytd_orc_range) else []
                ytd_orc = sum([x for x in ytd_orc_vals if x is not None])
                ytd_rxo_delta = round(ytd_2026 - ytd_orc, 1) if (ytd_2026 is not None and ytd_orc is not None) else None
                ytd_rxo_pct = round(((ytd_2026 - ytd_orc) / ytd_orc) * 100, 2) if (ytd_orc and ytd_orc > 0 and ytd_2026 is not None) else None

                base_real = parse_num(df_gr.iloc[r_gr, 4]) if df_gr.shape[0] > r_gr and df_gr.shape[1] > 4 else None
                base_orc = parse_num(df_gr.iloc[r_gr, 5]) if df_gr.shape[0] > r_gr and df_gr.shape[1] > 5 else None

                taxa_real = round((v_curr / base_real) * 100, 2) if (base_real and base_real > 0 and v_curr is not None) else None
                taxa_orc = round((v_orc / base_orc) * 100, 2) if (base_orc and base_orc > 0 and v_orc is not None) else None
                taxa_delta_pp = round(taxa_real - taxa_orc, 2) if (taxa_real is not None and taxa_orc is not None) else None

            d_mom = round(v_curr - v_mom, 1)
            pct_mom = round(((v_curr - v_mom) / v_mom) * 100, 2) if v_mom > 0 else 0

            d_yoy = round(v_curr - v_yoy, 1)
            pct_yoy = round(((v_curr - v_yoy) / v_yoy) * 100, 2) if v_yoy > 0 else 0

            cities_list.append({
                **cm,
                'vol_real': round(v_curr, 1),
                'vol_orc': round(v_orc, 1) if v_orc is not None else None,
                'rxo_delta': d_rxo,
                'rxo_pct': pct_rxo,
                'vol_ago26': round(v_mom, 1),
                'mom_delta': d_mom,
                'mom_pct': pct_mom,
                'vol_sep25': round(v_yoy, 1),
                'yoy_delta': d_yoy,
                'yoy_pct': pct_yoy,
                't1': round(v_p1, 1),
                't2': round(v_p2, 1),
                't3': round(v_p3, 1),
                't4': round(v_p4, 1),
                'ytd_real': round(ytd_2026, 1),
                'ytd_2025': round(ytd_2025, 1),
                'ytd_26x25_delta': ytd_26x25_delta,
                'ytd_26x25_pct': ytd_26x25_pct,
                'ytd_orc': round(ytd_orc, 1) if ytd_orc is not None else None,
                'ytd_rxo_delta': ytd_rxo_delta,
                'ytd_rxo_pct': ytd_rxo_pct,
                'base_real': int(base_real) if base_real else 0,
                'base_orc': int(base_orc) if base_orc else None,
                'taxa_real': taxa_real,
                'taxa_orc': taxa_orc,
                'taxa_delta_pp': taxa_delta_pp
            })

        timeline_list = []
        for idx, (m_iso, m_lbl) in enumerate(MONTH_NAMES):
            c = start_hist_col + idx
            
            r_tot = b_r + 0
            r_gm = b_r + 1
            r_md = b_r + 8
            
            v_tot = parse_num(df_ana.iloc[r_tot, c]) if df_ana.shape[1] > c else None
            v_gm = parse_num(df_ana.iloc[r_gm, c]) if df_ana.shape[1] > c else None
            v_md = parse_num(df_ana.iloc[r_md, c]) if df_ana.shape[1] > c else None
            
            if is_xlsb:
                v_orc_tot = None
                v_orc_gm = None
                v_orc_md = None
            else:
                c_orc = start_orc_hist_col + idx
                v_orc_tot = parse_num(df_ana.iloc[r_tot, c_orc]) if df_ana.shape[1] > c_orc else None
                v_orc_gm = parse_num(df_ana.iloc[r_gm, c_orc]) if df_ana.shape[1] > c_orc else None
                v_orc_md = parse_num(df_ana.iloc[r_md, c_orc]) if df_ana.shape[1] > c_orc else None

            c_dict = {}
            for i_cm, cm in enumerate(cities_meta):
                if cm['tipo'] == 'CIDADE':
                    r_c = b_r + i_cm
                    v_c = parse_num(df_ana.iloc[r_c, c]) if df_ana.shape[1] > c else None
                    v_orc_c = parse_num(df_ana.iloc[r_c, c_orc]) if (not is_xlsb and df_ana.shape[1] > c_orc) else None
                    c_dict[cm['id']] = {
                        'realizado': round(v_c, 1) if v_c is not None else None,
                        'orcamento': round(v_orc_c, 1) if v_orc_c is not None else None
                    }

            timeline_list.append({
                'iso': m_iso,
                'label': m_lbl,
                'realizado': round(v_tot, 1) if v_tot is not None else None,
                'orcamento': round(v_orc_tot, 1) if v_orc_tot is not None else None,
                'gm_real': round(v_gm, 1) if v_gm is not None else None,
                'md_real': round(v_md, 1) if v_md is not None else None,
                'gm_orc': round(v_orc_gm, 1) if v_orc_gm is not None else None,
                'md_orc': round(v_orc_md, 1) if v_orc_md is not None else None,
                'cities': c_dict
            })

        reg = cities_list[0]
        modes_data[mode_key] = {
            'key': mode_key,
            'label': mode_label,
            'summary': {
                'vol_real': reg['vol_real'],
                'vol_orc': reg['vol_orc'],
                'rxo_delta': reg['rxo_delta'],
                'rxo_pct': reg['rxo_pct'],
                'vol_ago26': reg['vol_ago26'],
                'mom_delta': reg['mom_delta'],
                'mom_pct': reg['mom_pct'],
                'vol_sep25': reg['vol_sep25'],
                'yoy_delta': reg['yoy_delta'],
                'yoy_pct': reg['yoy_pct'],
                't1': reg['t1'],
                't2': reg['t2'],
                't3': reg['t3'],
                't4': reg['t4'],
                'ytd_real': reg['ytd_real'],
                'ytd_2025': reg['ytd_2025'],
                'ytd_26x25_delta': reg['ytd_26x25_delta'],
                'ytd_26x25_pct': reg['ytd_26x25_pct'],
                'ytd_orc': reg['ytd_orc'],
                'ytd_rxo_delta': reg['ytd_rxo_delta'],
                'ytd_rxo_pct': reg['ytd_rxo_pct'],
                'base_real': reg['base_real'],
                'base_orc': reg['base_orc'],
                'taxa_real': reg['taxa_real'],
                'taxa_orc': reg['taxa_orc'],
                'taxa_delta_pp': reg['taxa_delta_pp']
            },
            'cities': cities_list,
            'timeline': timeline_list
        }

    bases_map = {c['id']: c['base_real'] for c in modes_data['TOTAL']['cities']}
    proj_invol = extract_involuntary_projection(is_pme=is_xlsb, bases_map=bases_map)
    cc_summary = extract_callcenter_summary(bases_map=bases_map)

    return {
        'segmento': segment_name,
        'mes_referencia': 'Outubro / 2026',
        'data_posicao': '01/10/2026',
        'tendencia_atual': '1ª Tendência (T1)',
        'default_mode': 'TOTAL',
        'modes': modes_data,
        'involuntaria_proj': proj_invol,
        'callcenter': cc_summary
    }

if __name__ == '__main__':
    data_total = extract_full_churn_data(resolve_data_file('1Tend_Out26_Acompanhamento Churn Horizontal_v13.xlsm'), 'Banda Larga Total', is_xlsb=False)
    data_pme = extract_full_churn_data(resolve_data_file('1Tend_Out26_Acompanhamento Churn Horizontal_PME_v2.xlsb'), 'Banda Larga PME', is_xlsb=True)

    os.makedirs('public/churn-bl-total', exist_ok=True)
    os.makedirs('public/churn-bl-pme', exist_ok=True)

    with open('public/churn-bl-total/data.json', 'w', encoding='utf-8') as f:
        json.dump(data_total, f, ensure_ascii=False, indent=2)

    with open('public/churn-bl-pme/data.json', 'w', encoding='utf-8') as f:
        json.dump(data_pme, f, ensure_ascii=False, indent=2)

    print("Success! Both data.json extracted with Out/26 (T1) and full histories integrated.")
