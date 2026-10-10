import openpyxl
import pyxlsb
import pandas as pd
import json
import os

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

months_keys = [
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

cc_months_meta = [
    ('2025-01', 'Jan/25', 0), ('2025-02', 'Fev/25', 1), ('2025-03', 'Mar/25', 2),
    ('2025-04', 'Abr/25', 3), ('2025-05', 'Mai/25', 4), ('2025-06', 'Jun/25', 5),
    ('2025-07', 'Jul/25', 6), ('2025-08', 'Ago/25', 7), ('2025-09', 'Set/25', 8),
    ('2025-10', 'Out/25', 9), ('2025-11', 'Nov/25', 10), ('2025-12', 'Dez/25', 11),
    ('2026-01', 'Jan/26', 12), ('2026-02', 'Fev/26', 13), ('2026-03', 'Mar/26', 14),
    ('2026-04', 'Abr/26', 15), ('2026-05', 'Mai/26', 16), ('2026-06', 'Jun/26', 17),
    ('2026-07', 'Jul/26', 18), ('2026-08', 'Ago/26', 19), ('2026-09', 'Set/26', 20)
]

def extract_involuntary_projection(is_pme=False):
    proj_path = 'MODELO_PROJEÇÃO_CIDADE_RESIDENCIAL - SET S4_V2.xlsb'
    sheet_name = 'ÁREA CABEADA PME' if is_pme else 'ÁREA CABEADA TOTAL'
    print(f"Lendo Modelo Projeção Involuntária de {sheet_name}...")
    df_proj = pd.read_excel(proj_path, engine='pyxlsb', sheet_name=sheet_name, header=None)

    # 1. Encontrar faixa de colunas da Banda Larga
    bl_start = 236
    bl_end = 466
    for c in range(df_proj.shape[1]):
        val = str(df_proj.iloc[1, c]).upper()
        if 'BANDA LARGA' in val: bl_start = c
        if 'TV' in val and c > bl_start:
            bl_end = c
            break

    # 2. Mapear colunas dos 21 meses
    col_map = {}
    for c in range(bl_start, bl_end):
        m = str(df_proj.iloc[2, c]).strip().lower()
        if m and m != 'nan':
            for iso, lbl, patterns in months_keys:
                if any(p in m for p in patterns):
                    col_map.setdefault(iso, []).append((c, m))

    final_month_cols = []
    for iso, lbl, patterns in months_keys:
        candidates = col_map.get(iso, [])
        if not candidates: continue
        best = None
        for c, m in candidates:
            if 'fech' in m: best = c; break
            if 's4' in m: best = c
        if best is None: best = candidates[-1][0]
        final_month_cols.append((iso, lbl, best))

    # Abertura Set/26 S4 (última coluna mapeada)
    col_set26 = final_month_cols[-1][2]
    r_rno = 11

    reg_fpd = parse_num(df_proj.iloc[r_rno, col_set26]) or 0
    reg_fraude = parse_num(df_proj.iloc[r_rno, col_set26+1]) or 0
    reg_base = parse_num(df_proj.iloc[r_rno, col_set26+2]) or 0
    reg_opcao = parse_num(df_proj.iloc[r_rno, col_set26+3]) or 0
    reg_total = parse_num(df_proj.iloc[r_rno, col_set26+4]) or (reg_fpd + reg_fraude + reg_base + reg_opcao)

    # 3. Mapear cidades
    city_rows = {}
    for r in range(21, df_proj.shape[0]):
        reg_val = df_proj.iloc[r, 3]
        if str(reg_val).strip().upper() == 'RNO':
            c_name = df_proj.iloc[r, 1]
            cid = normalize_city_id(c_name)
            city_rows[cid] = r

    cities_proj = {}
    for cid, r in city_rows.items():
        fpd = parse_num(df_proj.iloc[r, col_set26]) or 0
        fraude = parse_num(df_proj.iloc[r, col_set26+1]) or 0
        invol_base = parse_num(df_proj.iloc[r, col_set26+2]) or 0
        opcao = parse_num(df_proj.iloc[r, col_set26+3]) or 0
        total = parse_num(df_proj.iloc[r, col_set26+4]) or (fpd + fraude + invol_base + opcao)
        cities_proj[cid] = {
            'fpd': round(fpd, 1),
            'fraude': round(fraude, 1),
            'invol_base': round(invol_base, 1),
            'opcao': round(opcao, 1),
            'total': round(total, 1)
        }

    gm_cities = ['ANANINDEUA', 'BELEM', 'MACAPA', 'MANAUS', 'SANTANA', 'SAO_LUIS']
    md_cities = ['CASTANHAL', 'CAXIAS', 'IMPERATRIZ', 'MARABA', 'PARAGOMINAS', 'PARAUAPEBAS', 'TIMON']

    def calc_group_proj(keys):
        tot = {'fpd': 0, 'fraude': 0, 'invol_base': 0, 'opcao': 0, 'total': 0}
        for k in keys:
            if k in cities_proj:
                for f in tot: tot[f] += cities_proj[k][f]
        return {f: round(tot[f], 1) for f in tot}

    gm_proj = calc_group_proj(gm_cities)
    md_proj = calc_group_proj(md_cities)

    # 4. Histórico 21 meses das Aberturas do Involuntário (Regional, GM, MD)
    invol_history = []
    for iso, lbl, c in final_month_cols:
        h_fpd = parse_num(df_proj.iloc[r_rno, c]) or 0
        h_fraude = parse_num(df_proj.iloc[r_rno, c+1]) or 0
        h_base = parse_num(df_proj.iloc[r_rno, c+2]) or 0
        h_opcao = parse_num(df_proj.iloc[r_rno, c+3]) or 0
        h_total = parse_num(df_proj.iloc[r_rno, c+4]) or (h_fpd + h_fraude + h_base + h_opcao)

        # GM e MD sums
        gm_tot = {'fpd': 0, 'fraude': 0, 'invol_base': 0, 'opcao': 0, 'total': 0}
        md_tot = {'fpd': 0, 'fraude': 0, 'invol_base': 0, 'opcao': 0, 'total': 0}
        for g_c in gm_cities:
            if g_c in city_rows:
                r_c = city_rows[g_c]
                gm_tot['fpd'] += parse_num(df_proj.iloc[r_c, c]) or 0
                gm_tot['fraude'] += parse_num(df_proj.iloc[r_c, c+1]) or 0
                gm_tot['invol_base'] += parse_num(df_proj.iloc[r_c, c+2]) or 0
                gm_tot['opcao'] += parse_num(df_proj.iloc[r_c, c+3]) or 0
                gm_tot['total'] += parse_num(df_proj.iloc[r_c, c+4]) or 0
        for m_c in md_cities:
            if m_c in city_rows:
                r_c = city_rows[m_c]
                md_tot['fpd'] += parse_num(df_proj.iloc[r_c, c]) or 0
                md_tot['fraude'] += parse_num(df_proj.iloc[r_c, c+1]) or 0
                md_tot['invol_base'] += parse_num(df_proj.iloc[r_c, c+2]) or 0
                md_tot['opcao'] += parse_num(df_proj.iloc[r_c, c+3]) or 0
                md_tot['total'] += parse_num(df_proj.iloc[r_c, c+4]) or 0

        invol_history.append({
            'iso': iso,
            'label': lbl,
            'fpd': round(h_fpd, 1),
            'fraude': round(h_fraude, 1),
            'invol_base': round(h_base, 1),
            'opcao': round(h_opcao, 1),
            'total': round(h_total, 1),
            'gm': {k: round(v, 1) for k, v in gm_tot.items()},
            'md': {k: round(v, 1) for k, v in md_tot.items()}
        })

    return {
        'regional': {
            'fpd': round(reg_fpd, 1),
            'fraude': round(reg_fraude, 1),
            'invol_base': round(reg_base, 1),
            'opcao': round(reg_opcao, 1),
            'total': round(reg_total, 1),
            'pct_base': round((reg_base / reg_total * 100), 1) if reg_total > 0 else 0,
            'pct_fpd': round((reg_fpd / reg_total * 100), 1) if reg_total > 0 else 0,
            'pct_opcao': round((reg_opcao / reg_total * 100), 1) if reg_total > 0 else 0,
            'pct_fraude': round((reg_fraude / reg_total * 100), 1) if reg_total > 0 else 0
        },
        'gm': gm_proj,
        'md': md_proj,
        'cities': cities_proj,
        'history': invol_history
    }

print("Testing extract_involuntary_projection...")
res_tot = extract_involuntary_projection(False)
print("Total history len:", len(res_tot['history']))
print("First month:", res_tot['history'][0])
print("Last month:", res_tot['history'][-1])
