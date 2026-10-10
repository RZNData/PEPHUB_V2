import pandas as pd

df_pme = pd.read_excel('MODELO_PROJEÇÃO_CIDADE_RESIDENCIAL - SET S4_V2.xlsb', engine='pyxlsb', sheet_name='ÁREA CABEADA PME', header=None, nrows=15)

# Check col 236 to 465 in row 2 and 3
cols_to_check = [236, 276, 295, 305, 335, 360, 385, 415, 440, 460]
for c in cols_to_check:
    m = df_pme.iloc[2, c]
    sub = [str(df_pme.iloc[3, c+k]) for k in range(5)]
    val_r11 = [df_pme.iloc[11, c+k] for k in range(5)]
    print(f"PME Col {c}: m='{m}', sub={sub}, RNO={val_r11}")
