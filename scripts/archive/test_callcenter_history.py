import pandas as pd

df = pd.read_excel('SUMÁRIO - CALL CENTER - S4 - 092026.xlsb', engine='pyxlsb', sheet_name='Base', header=None)

# Let's inspect row 2 (months):
months = []
for c in range(6, 27):
    m = df.iloc[2, c]
    months.append((c, str(m).strip()))

print("Call Center Months (cols 6 to 26):", months)

# Let's check row labels in col 3 or col 4
for r in [287, 285, 286, 278, 272, 273]:
    print(f"Row {r}: col 3='{df.iloc[r, 3]}', col 4='{df.iloc[r, 4]}'")

# Check indicator columns offset
# Motives:
# Financeiro: col 363 (mix), col 489 (taxa os)
# Concorrência: col 384 (mix), col 510 (taxa os)
# Canc Auto: col 405 (mix), col 531 (taxa os)
# Técnico: col 426 (mix), col 552 (taxa os)
# Mudança de Endereço: col 447 (mix), col 573 (taxa os)
# Atendimento: col 468 (mix), col 594 (taxa os)

motives = [
    ('financeiro', 'Financeiro', 363, 489),
    ('canc_auto', 'Canc. Automático', 405, 531),
    ('concorrencia', 'Concorrência', 384, 510),
    ('me', 'Mudança de Endereço', 447, 573),
    ('tecnico', 'Técnico', 426, 552),
    ('atendimento', 'Atendimento', 468, 594),
]

print("\nRegional Norte (row 287) values for Set/26 (offset +20):")
for mid, name, c_mix, c_tx in motives:
    v_mix = df.iloc[287, c_mix + 20]
    v_tx = df.iloc[287, c_tx + 20]
    print(f"{name:20s}: Mix={v_mix*100:.1f}%, Tx OS={v_tx*100:.1f}%")
