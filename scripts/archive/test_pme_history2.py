import pandas as pd

df_pme = pd.read_excel('MODELO_PROJEÇÃO_CIDADE_RESIDENCIAL - SET S4_V2.xlsb', engine='pyxlsb', sheet_name='ÁREA CABEADA PME', header=None)

# Let's locate the 21 months in row 2 of PME
months_cols_pme = []
for c in range(200, 470):
    m = df_pme.iloc[2, c]
    sub = df_pme.iloc[3, c]
    if pd.notna(m) and str(m).strip() != '':
        # print(f"c={c}: {m}")
        pass

# Let's test if the same column positions or matching months work:
print("PME r_rno=11:")
for c in [236, 241, 246, 251, 256, 261, 266, 271, 276, 281, 286, 291, 296, 301, 306, 336, 361, 386, 416, 441, 461]:
    m = df_pme.iloc[2, c] if pd.notna(df_pme.iloc[2, c]) else df_pme.iloc[2, c-1]
    tot = df_pme.iloc[11, c+4] if c+4 < df_pme.shape[1] else None
    print(f"c={c}: m='{m}', row11={[df_pme.iloc[11, c+k] for k in range(5)]}")
