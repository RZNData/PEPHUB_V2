import pandas as pd

df = pd.read_excel('MODELO_PROJEÇÃO_CIDADE_RESIDENCIAL - SET S4_V2.xlsb', engine='pyxlsb', sheet_name='ÁREA CABEADA TOTAL', header=None, nrows=5)

for c in range(290, 465, 5):
    m = df.iloc[2, c]
    sub = [str(df.iloc[3, c+k]) for k in range(5)]
    print(f"Col {c}: m='{m}', subs={sub}")
