import pandas as pd

# Involuntary columns mapped from earlier:
# 21 months: Jan/25 to Set/26
invol_months_cols = [
    ('2025-01', 'Jan/25', 236),
    ('2025-02', 'Fev/25', 241),
    ('2025-03', 'Mar/25', 246),
    ('2025-04', 'Abr/25', 251),
    ('2025-05', 'Mai/25', 256),
    ('2025-06', 'Jun/25', 261),
    ('2025-07', 'Jul/25', 266),
    ('2025-08', 'Ago/25', 271),
    ('2025-09', 'Set/25', 276),
    ('2025-10', 'Out/25', 281),
    ('2025-11', 'Nov/25', 286),
    ('2025-12', 'Dez/25', 291),
    ('2026-01', 'Jan/26', 295),
    ('2026-02', 'Fev/26', 300),
    ('2026-03', 'Mar/26', 305),
    ('2026-04', 'Abr/26', 335),
    ('2026-05', 'Mai/26', 360),
    ('2026-06', 'Jun/26', 385),
    ('2026-07', 'Jul/26', 415),
    ('2026-08', 'Ago/26', 440),
    ('2026-09', 'Set/26', 460)
]

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

df_tot = pd.read_excel('MODELO_PROJEÇÃO_CIDADE_RESIDENCIAL - SET S4_V2.xlsb', engine='pyxlsb', sheet_name='ÁREA CABEADA TOTAL', header=None)

r_rno = 11 # Regional Norte
tot_history = []
for iso, lbl, col in invol_months_cols:
    fpd = parse_num(df_tot.iloc[r_rno, col]) or 0
    fraude = parse_num(df_tot.iloc[r_rno, col+1]) or 0
    base = parse_num(df_tot.iloc[r_rno, col+2]) or 0
    opcao = parse_num(df_tot.iloc[r_rno, col+3]) or 0
    total = parse_num(df_tot.iloc[r_rno, col+4]) or (fpd + fraude + base + opcao)
    tot_history.append({
        'iso': iso,
        'label': lbl,
        'fpd': round(fpd, 1),
        'fraude': round(fraude, 1),
        'invol_base': round(base, 1),
        'opcao': round(opcao, 1),
        'total': round(total, 1)
    })

print(f"Total Involuntary History: {len(tot_history)} months.")
print("Sample first month:", tot_history[0])
print("Sample Set/25 month:", tot_history[8])
print("Sample last month (Set/26):", tot_history[-1])
