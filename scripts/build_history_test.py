import pandas as pd
import json

# 1. Test Call Center History (21 months: Jan/25 to Set/26)
df_cc = pd.read_excel('SUMÁRIO - CALL CENTER - S4 - 092026.xlsb', engine='pyxlsb', sheet_name='Base', header=None)

cc_months_meta = [
    ('2025-01', 'Jan/25', 0), ('2025-02', 'Fev/25', 1), ('2025-03', 'Mar/25', 2),
    ('2025-04', 'Abr/25', 3), ('2025-05', 'Mai/25', 4), ('2025-06', 'Jun/25', 5),
    ('2025-07', 'Jul/25', 6), ('2025-08', 'Ago/25', 7), ('2025-09', 'Set/25', 8),
    ('2025-10', 'Out/25', 9), ('2025-11', 'Nov/25', 10), ('2025-12', 'Dez/25', 11),
    ('2026-01', 'Jan/26', 12), ('2026-02', 'Fev/26', 13), ('2026-03', 'Mar/26', 14),
    ('2026-04', 'Abr/26', 15), ('2026-05', 'Mai/26', 16), ('2026-06', 'Jun/26', 17),
    ('2026-07', 'Jul/26', 18), ('2026-08', 'Ago/26', 19), ('2026-09', 'Set/26', 20)
]

motives_config = [
    {'id': 'financeiro', 'nome': 'Financeiro', 'col_mix': 363, 'col_tx': 489, 'color': '#2a5d8f'},
    {'id': 'canc_auto', 'nome': 'Cancelamento Automático', 'col_mix': 405, 'col_tx': 531, 'color': '#c0392b'},
    {'id': 'concorrencia', 'nome': 'Concorrência', 'col_mix': 384, 'col_tx': 510, 'color': '#c98a15'},
    {'id': 'me', 'nome': 'Mudança de Endereço', 'col_mix': 447, 'col_tx': 573, 'color': '#8a0f18'},
    {'id': 'tecnico', 'nome': 'Técnico', 'col_mix': 426, 'col_tx': 552, 'color': '#516173'},
    {'id': 'atendimento', 'nome': 'Atendimento', 'col_mix': 468, 'col_tx': 594, 'color': '#6b4b8a'}
]

r_rno = 287 # Regional Norte

def parse_num(v):
    if v is None or pd.isna(v): return None
    s = str(v).strip().replace(' ', '')
    if s in ['', '-', '#DIV/0!', 'nan', 'None']: return None
    if '.' in s and ',' not in s:
        parts = s.split('.')
        if len(parts) == 2 and len(parts[1]) == 3: s = s.replace('.', '')
    elif ',' in s: s = s.replace('.', '').replace(',', '.')
    try: return float(s)
    except: return None

cc_history = []
for iso, lbl, offset in cc_months_meta:
    item = {'iso': iso, 'label': lbl, 'mix': {}, 'taxa_os': {}}
    for m in motives_config:
        v_mix = parse_num(df_cc.iloc[r_rno, m['col_mix'] + offset])
        v_tx = parse_num(df_cc.iloc[r_rno, m['col_tx'] + offset])
        item['mix'][m['id']] = round(v_mix * 100, 1) if v_mix is not None else None
        item['taxa_os'][m['id']] = round(v_tx * 100, 1) if v_tx is not None else None
    cc_history.append(item)

print(f"CC History extracted: {len(cc_history)} months.")
print("Sample first month:", cc_history[0])
print("Sample last month:", cc_history[-1])
