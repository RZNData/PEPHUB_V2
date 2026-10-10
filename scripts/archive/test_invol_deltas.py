import pandas as pd
from test_dynamic_map import months_keys

df = pd.read_excel('MODELO_PROJEÇÃO_CIDADE_RESIDENCIAL - SET S4_V2.xlsb', engine='pyxlsb', sheet_name='ÁREA CABEADA TOTAL', header=None)

# Set/26 is col 460
# Ago/26 Fech is col 440
# Set/25 Fech is col 276
col_set26 = 460
col_ago26 = 440
col_set25 = 276

r_rno = 11

def get_pillars(r, col):
    fpd = df.iloc[r, col] or 0
    fraude = df.iloc[r, col+1] or 0
    base = df.iloc[r, col+2] or 0
    opcao = df.iloc[r, col+3] or 0
    total = df.iloc[r, col+4] or (fpd + fraude + base + opcao)
    return {'fpd': fpd, 'fraude': fraude, 'invol_base': base, 'opcao': opcao, 'total': total}

p_set26 = get_pillars(r_rno, col_set26)
p_ago26 = get_pillars(r_rno, col_ago26)
p_set25 = get_pillars(r_rno, col_set25)

print("Regional Norte Involuntary:")
print("Set/26:", p_set26)
print("Ago/26:", p_ago26)
print("Set/25:", p_set25)

for k in ['invol_base', 'fpd', 'opcao', 'fraude', 'total']:
    v_s26 = p_set26[k]
    v_a26 = p_ago26[k]
    v_s25 = p_set25[k]
    mom = ((v_s26 - v_a26) / v_a26 * 100) if v_a26 > 0 else 0
    yoy = ((v_s26 - v_s25) / v_s25 * 100) if v_s25 > 0 else 0
    pct_tot = (v_s26 / p_set26['total'] * 100) if p_set26['total'] > 0 else 0
    print(f"  {k:12s}: Vol={v_s26:6.1f}, %Total={pct_tot:5.1f}%, MoM={mom:+6.1f}%, YoY={yoy:+6.1f}%")
