import pandas as pd
import json

df_base = pd.read_excel('SUMÁRIO - CALL CENTER - S4 - 092026.xlsb', engine='pyxlsb', sheet_name='Base', header=None)
df_cc = df_base

# 9 months of Speech Analytics in 2026:
# Jan: 692-700
# Fev: 701-709
# Mar: 710-718
# Abr: 719-727
# Mai: 728-736
# Jun: 737-745
# Jul: 746-754
# Ago: 755-763
# Set: 764-772

speech_months = [
    ('2026-01', 'Jan/26', 692),
    ('2026-02', 'Fev/26', 701),
    ('2026-03', 'Mar/26', 710),
    ('2026-04', 'Abr/26', 719),
    ('2026-05', 'Mai/26', 728),
    ('2026-06', 'Jun/26', 737),
    ('2026-07', 'Jul/26', 746),
    ('2026-08', 'Ago/26', 755),
    ('2026-09', 'Set/26', 764)
]

speech_names = [
    ('acha_caro', 'Acha Caro / Reclama de Valor', 0, '#c0392b'),
    ('reajuste', 'Reajuste de Valor', 1, '#c98a15'),
    ('pouca_util', 'Sem / Pouca Utilização', 2, '#516173'),
    ('nao_pedi', 'Não Pedi / Não Solicitei', 3, '#6b4b8a'),
    ('tecnico', 'Técnico - Internet', 4, '#2a5d8f'),
    ('concorrencia', 'Concorrência', 5, '#e23a1e'),
    ('dif_financ', 'Dificuldade Financeira', 6, '#8a0f18'),
    ('nao_concorda', 'Não Concorda / Consulta Valores', 7, '#1b2430'),
    ('me', 'Mudança de Endereço', 8, '#9b1c1c')
]

r_rno = 287

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

# Extract timeline for Regional Norte
speech_history = []
for iso, lbl, col_start in speech_months:
    item = {'iso': iso, 'label': lbl, 'speeches': {}}
    for sid, sname, offset, color in speech_names:
        val = parse_num(df_base.iloc[r_rno, col_start + offset]) or 0
        item['speeches'][sid] = round(val * 100, 1)
    speech_history.append(item)

print(f"Speech history extracted: {len(speech_history)} months.")
print("Jan/26:", speech_history[0])
print("Set/26:", speech_history[-1])

# Calculate Set/26 summary with MoM and YTD deltas
speech_summary = []
set_item = speech_history[-1]['speeches']
ago_item = speech_history[-2]['speeches']
jan_item = speech_history[0]['speeches']

for sid, sname, offset, color in speech_names:
    v_set = set_item[sid]
    v_ago = ago_item[sid]
    v_jan = jan_item[sid]
    mom = round(v_set - v_ago, 1)
    ytd = round(v_set - v_jan, 1)
    speech_summary.append({
        'id': sid,
        'speech': sname,
        'color': color,
        'pct': v_set,
        'mom_pp': mom,
        'ytd_pp': ytd
    })

speech_summary.sort(key=lambda x: x['pct'], reverse=True)
print("\nSpeech Summary Set/26 (Ranking):")
for s in speech_summary:
    print(f"  {s['speech']:32s}: {s['pct']:4.1f}% (MoM: {s['mom_pp']:+4.1f} pp, YTD: {s['ytd_pp']:+4.1f} pp)")
